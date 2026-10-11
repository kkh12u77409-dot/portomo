/* ==========================================================================
   لوحة الأدوات الشخصية — script.js
   --------------------------------------------------------------------------
   يكتشف الصفحة الحالية ويشغّل الأداة المناسبة فقط.
   ========================================================================== */
(function () {
  'use strict';

  /* ========================================================================
     1) أدوات مساعدة عامة
     ======================================================================== */

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => Array.from(ctx.querySelectorAll(sel));

  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function showError(element, message) {
    if (!element) return;
    element.textContent = message;
    element.hidden = false;
  }

  function clearError(element) {
    if (!element) return;
    element.textContent = '';
    element.hidden = true;
  }

  const statusTimers = new WeakMap();

  function setStatus(element, message, type = 'ok', autoHide = 4000) {
    if (!element) return;
    const prev = statusTimers.get(element);
    if (prev) clearTimeout(prev);
    element.textContent = message;
    element.className = `status status--${type}`;
    element.hidden = !message;
    if (message && autoHide > 0) {
      statusTimers.set(element, setTimeout(() => {
        element.textContent = '';
        element.hidden = true;
      }, autoHide));
    }
  }

  function clamp(v, min, max) { return Math.min(Math.max(v, min), max); }

  function formatNumber(value) {
    if (!Number.isFinite(value)) return '—';
    return String(Math.round(value * 1e10) / 1e10);
  }

  async function copyText(text) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return true;
      }
    } catch (_) {}
    try {
      const area = document.createElement('textarea');
      area.value = text;
      area.setAttribute('readonly', '');
      area.style.cssText = 'position:fixed;top:-9999px';
      document.body.appendChild(area);
      area.select();
      const ok = document.execCommand('copy');
      document.body.removeChild(area);
      return ok;
    } catch (_) { return false; }
  }

  /* ========================================================================
     2) الوضع الفاتح / الداكن
     ======================================================================== */
  const THEME_KEY = 'toolbox_theme_v1';

  function getTheme() {
    const saved = (() => { try { return localStorage.getItem(THEME_KEY); } catch (_) { return null; } })();
    if (saved === 'dark' || saved === 'light') return saved;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    const btn = $('#themeToggle');
    if (btn) {
      btn.setAttribute('aria-pressed', String(theme === 'dark'));
      btn.title = theme === 'dark' ? 'التبديل إلى الوضع الفاتح' : 'التبديل إلى الوضع الداكن';
    }
    try { localStorage.setItem(THEME_KEY, theme); } catch (_) {}
  }

  function initTheme() {
    applyTheme(getTheme());
    const btn = $('#themeToggle');
    if (btn) btn.addEventListener('click', () => applyTheme(getTheme() === 'dark' ? 'light' : 'dark'));
  }

  /* ========================================================================
     3) عناصر مشتركة (السنة في التذييل، حركة ظهور البطاقات)
     ======================================================================== */
  function initCommon() {
    /* السنة في التذييل */
    const yearEl = $('#year');
    if (yearEl) yearEl.textContent = String(new Date().getFullYear());

    /* ظهور تدريجي للبطاقات عند التمرير */
    const items = $$('.reveal');
    if (!items.length) return;

    items.forEach((item, i) => {
      const delay = clamp(i, 0, 6) * 80;
      item.style.transitionDelay = `${delay}ms`;
    });

    if (typeof IntersectionObserver !== 'function') {
      items.forEach(item => { item.classList.add('is-visible'); item.style.transitionDelay = ''; });
      return;
    }

    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        io.unobserve(entry.target);
        const delay = parseFloat(entry.target.style.transitionDelay) || 0;
        setTimeout(() => { entry.target.style.transitionDelay = ''; }, delay * 1000 + 700);
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -30px 0px' });

    items.forEach(item => io.observe(item));
  }

  /* ========================================================================
     4) الآلة الحاسبة
     ======================================================================== */
  const Calculator = {
    expression: '',
    result: '0',

    init() {
      this.exprEl   = $('#calc-expression');
      this.resultEl = $('#calc-result');
      this.errorEl  = $('#calc-error');
      this.screenEl = $('#calc-screen');
      this.widget   = $('#calc-widget');
      if (!this.widget) return;

      this.widget.addEventListener('click', (e) => {
        const key = e.target.closest('[data-calc]');
        if (key) this.press(key.dataset.calc);
      });

      document.addEventListener('keydown', (e) => {
        const active = document.activeElement;
        if (!active.closest('#calc-widget') && active !== this.screenEl) return;
        const map = {
          Enter:'=', '=':'=', Backspace:'backspace', Escape:'clear',
          '+':'+', '-':'-', '*':'*', '/':'/',
          '^':'^', '%':'%', '(':'(', ')':')', '.':'.', ',':'.',
        };
        const action = map[e.key] ?? ((e.key >= '0' && e.key <= '9') ? e.key : null);
        if (action) { e.preventDefault(); this.press(action); }
      });

      this.render();
    },

    press(key) {
      clearError(this.errorEl);
      switch (key) {
        case 'clear':     this.expression = ''; this.result = '0'; break;
        case 'backspace': this.expression = this.expression.slice(0, -1); break;
        case '=':         this.evaluate(); return;
        case 'sqrt':      this.expression += 'sqrt('; break;
        default:          this.expression += key;
      }
      this.render();
    },

    render() {
      if (this.exprEl)   this.exprEl.textContent   = this.expression || '\u00a0';
      if (this.resultEl) this.resultEl.textContent  = this.result;
    },

    evaluate() {
      const expr = this.expression.trim();
      if (!expr) { showError(this.errorEl, 'أدخل تعبيرًا حسابيًا أولًا.'); return; }
      try {
        const val = this.parse(expr);
        if (!Number.isFinite(val)) throw new Error('inf');
        this.result = formatNumber(val);
        this.expression = String(val);
      } catch (err) {
        showError(this.errorEl, err.message === 'inf'
          ? 'خطأ: القسمة على صفر أو نتيجة غير محدودة.'
          : 'تعبير غير صالح — تحقق من الأقواس والعوامل.');
      }
      this.render();
    },

    /* Shunting-Yard آمن بدون eval */
    tokenize(expr) {
      const tokens = [];
      let i = 0;
      while (i < expr.length) {
        const ch = expr[i];
        if (/\s/.test(ch)) { i++; continue; }
        if (/[0-9]/.test(ch) || (ch === '.' && /[0-9]/.test(expr[i+1] ?? ''))) {
          let n = '';
          while (i < expr.length && /[0-9.]/.test(expr[i])) n += expr[i++];
          tokens.push(Number(n));
        } else if (expr.slice(i, i+4) === 'sqrt') {
          tokens.push('sqrt'); i += 4;
        } else if ('+-*/%^()'.includes(ch)) {
          tokens.push(ch); i++;
        } else { throw new Error('token'); }
      }
      return tokens;
    },

    parse(expr) {
      const tokens = this.tokenize(expr);
      const out = [], ops = [];
      const prec  = {'+':1,'-':1,'*':2,'/':2,'%':2,'^':3};
      const right = new Set(['^']);

      const apply = () => {
        const op = ops.pop();
        if (op === 'u-')   { out.push(-out.pop()); return; }
        if (op === 'sqrt') {
          const a = out.pop();
          if (a < 0) throw new Error('sqrt');
          out.push(Math.sqrt(a)); return;
        }
        const b = out.pop(), a = out.pop();
        if      (op === '+') out.push(a + b);
        else if (op === '-') out.push(a - b);
        else if (op === '*') out.push(a * b);
        else if (op === '/') { if (b === 0) throw new Error('inf'); out.push(a / b); }
        else if (op === '%') { if (b === 0) throw new Error('inf'); out.push(a % b); }
        else if (op === '^') out.push(Math.pow(a, b));
      };

      let expectOperand = true;
      for (const tok of tokens) {
        if (typeof tok === 'number') { out.push(tok); expectOperand = false; }
        else if (tok === 'sqrt')     { ops.push('sqrt'); }
        else if (tok === '(')        { ops.push('('); expectOperand = true; }
        else if (tok === ')') {
          while (ops.length && ops[ops.length-1] !== '(') apply();
          if (!ops.length) throw new Error('paren');
          ops.pop();
          if (ops[ops.length-1] === 'sqrt') apply();
          expectOperand = false;
        } else {
          const op = (tok === '-' && expectOperand) ? 'u-' : tok;
          if (op !== 'u-') {
            while (ops.length && ops[ops.length-1] !== '(' &&
                   ops[ops.length-1] !== 'sqrt' && ops[ops.length-1] !== 'u-' &&
                   (prec[ops[ops.length-1]] > prec[op] ||
                    (prec[ops[ops.length-1]] === prec[op] && !right.has(op)))) {
              apply();
            }
          }
          ops.push(op); expectOperand = true;
        }
      }
      while (ops.length) {
        if (ops[ops.length-1] === '(') throw new Error('paren');
        apply();
      }
      if (out.length !== 1) throw new Error('invalid');
      return out[0];
    },
  };

  /* ========================================================================
     5) تحويل حالة النص
     ======================================================================== */
  const CaseConverter = {
    init() {
      this.input    = $('#case-input');
      this.output   = $('#case-output');
      this.statusEl = $('#case-status');
      if (!this.input) return;

      $('#case-upper')   ?.addEventListener('click', () => this.convert('upper'));
      $('#case-lower')   ?.addEventListener('click', () => this.convert('lower'));
      $('#case-title')   ?.addEventListener('click', () => this.convert('title'));
      $('#case-sentence')?.addEventListener('click', () => this.convert('sentence'));

      $('#case-copy')?.addEventListener('click', async () => {
        const text = this.output?.value;
        if (!text) { setStatus(this.statusEl, 'لا يوجد نص للنسخ.', 'error'); return; }
        const ok = await copyText(text);
        setStatus(this.statusEl, ok ? '✓ تم النسخ.' : 'تعذّر النسخ.', ok ? 'ok' : 'error');
      });

      $('#case-clear')?.addEventListener('click', () => {
        this.input.value = '';
        if (this.output) this.output.value = '';
        setStatus(this.statusEl, '', 'ok', 0);
      });
    },

    convert(mode) {
      const text = this.input.value;
      if (!text.trim()) { setStatus(this.statusEl, 'أدخل نصًا أولًا.', 'error'); return; }
      let result = '';
      if      (mode === 'upper')    result = text.toUpperCase();
      else if (mode === 'lower')    result = text.toLowerCase();
      else if (mode === 'title')    result = text.replace(/\b\w/g, c => c.toUpperCase());
      else if (mode === 'sentence') result = text.toLowerCase().replace(/(^\s*\w|[.!?]\s+\w)/g, c => c.toUpperCase());
      if (this.output) this.output.value = result;
      setStatus(this.statusEl, '', 'ok', 0);
    },
  };

  /* ========================================================================
     6) عدّاد الكلمات والحروف
     ======================================================================== */
  const TextCounter = {
    init() {
      this.input = $('#counter-input');
      if (!this.input) return;
      this.words     = $('#cnt-words');
      this.chars     = $('#cnt-chars');
      this.charsNoSp = $('#cnt-chars-no-space');
      this.sentences = $('#cnt-sentences');
      this.paras     = $('#cnt-paragraphs');
      this.readtime  = $('#cnt-readtime');
      this.input.addEventListener('input', () => this.update());
      this.update();
    },

    update() {
      const text = this.input.value;
      const wordCount = text.trim() ? text.trim().split(/\s+/).length : 0;
      const charCount = text.length;
      const charNoSp  = text.replace(/\s/g, '').length;
      const sentCount = text.trim()
        ? (text.match(/[.!?؟]+/g) ?? []).length || 1
        : 0;
      const paraCount = text.trim()
        ? text.trim().split(/\n{2,}/).filter(p => p.trim()).length || 1
        : 0;

      const secs = Math.round((wordCount / 200) * 60);
      const readLabel = secs === 0 ? '< ١ ث'
        : secs < 60 ? `${secs} ث`
        : `${Math.ceil(secs / 60)} د`;

      if (this.words)     this.words.textContent     = wordCount;
      if (this.chars)     this.chars.textContent     = charCount;
      if (this.charsNoSp) this.charsNoSp.textContent = charNoSp;
      if (this.sentences) this.sentences.textContent = sentCount;
      if (this.paras)     this.paras.textContent     = paraCount;
      if (this.readtime)  this.readtime.textContent  = readLabel;
    },
  };

  /* ========================================================================
     7) المؤقت
     ======================================================================== */
  const Timer = {
    totalMs: 0, remainMs: 0,
    startedAt: null, rafId: null,
    state: 'idle', /* idle | running | paused | done */

    init() {
      this.widget   = $('#timer-widget');
      this.display  = $('#timer-display');
      this.barFill  = $('#timer-bar-fill');
      this.barEl    = this.barFill?.parentElement;
      this.errorEl  = $('#timer-error');
      this.btnStart = $('#timer-start');
      this.btnPause = $('#timer-pause');
      this.btnReset = $('#timer-reset');
      this.minsEl   = $('#timer-minutes');
      this.secsEl   = $('#timer-seconds');
      if (!this.widget) return;

      this.btnStart?.addEventListener('click', () => this.start());
      this.btnPause?.addEventListener('click', () => this.togglePause());
      this.btnReset?.addEventListener('click', () => this.reset());

      $$('[data-timer-preset]').forEach(btn => {
        btn.addEventListener('click', () => {
          const sec = parseInt(btn.dataset.timerPreset, 10);
          if (this.minsEl) this.minsEl.value = Math.floor(sec / 60);
          if (this.secsEl) this.secsEl.value = sec % 60;
          if (this.state !== 'idle') this.reset();
        });
      });

      this.render(0, 1);
    },

    totalFromInputs() {
      const m = clamp(parseInt(this.minsEl?.value || '0', 10), 0, 99);
      const s = clamp(parseInt(this.secsEl?.value || '0', 10), 0, 59);
      return (m * 60 + s) * 1000;
    },

    start() {
      clearError(this.errorEl);
      this.totalMs = this.totalFromInputs();
      if (this.totalMs <= 0) { showError(this.errorEl, 'أدخل وقتًا أكبر من صفر.'); return; }
      this.remainMs  = this.totalMs;
      this.startedAt = Date.now();
      this.state     = 'running';
      this.widget?.classList.add('is-running');
      this.widget?.classList.remove('is-done');
      this.updateButtons();
      this.tick();
    },

    togglePause() {
      if (this.state === 'running') {
        this.state = 'paused';
        cancelAnimationFrame(this.rafId);
        this.widget?.classList.remove('is-running');
      } else if (this.state === 'paused') {
        this.state = 'running';
        this.startedAt = Date.now() - (this.totalMs - this.remainMs);
        this.widget?.classList.add('is-running');
        this.tick();
      }
      this.updateButtons();
    },

    reset() {
      cancelAnimationFrame(this.rafId);
      this.state = 'idle';
      this.remainMs = 0;
      this.widget?.classList.remove('is-running', 'is-done');
      this.render(0, 1);
      this.updateButtons();
    },

    tick() {
      if (this.state !== 'running') return;
      const elapsed  = Date.now() - this.startedAt;
      this.remainMs  = Math.max(this.totalMs - elapsed, 0);
      this.render(this.remainMs, this.totalMs);
      if (this.remainMs <= 0) { this.done(); return; }
      this.rafId = requestAnimationFrame(() => this.tick());
    },

    done() {
      this.state = 'done';
      this.widget?.classList.remove('is-running');
      this.widget?.classList.add('is-done');
      this.updateButtons();
      this.beep();
    },

    render(remain, total) {
      const t  = Math.ceil(remain / 1000);
      const mm = String(Math.floor(t / 60)).padStart(2, '0');
      const ss = String(t % 60).padStart(2, '0');
      if (this.display) this.display.textContent = `${mm}:${ss}`;
      const pct = total > 0 ? (1 - remain / total) * 100 : 0;
      if (this.barFill) this.barFill.style.width = `${100 - pct}%`;
      if (this.barEl)   this.barEl.setAttribute('aria-valuenow', String(Math.round(100 - pct)));
    },

    updateButtons() {
      const active = this.state === 'running' || this.state === 'paused';
      const paused = this.state === 'paused';
      if (this.btnStart) this.btnStart.disabled = active;
      if (this.btnPause) {
        this.btnPause.disabled = !active;
        this.btnPause.textContent = paused ? '▶ استئناف' : '⏸ إيقاف مؤقت';
      }
      if (this.btnReset) this.btnReset.disabled = this.state === 'idle';
    },

    beep() {
      try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        [0, 220, 440].forEach(delay => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.connect(gain); gain.connect(ctx.destination);
          osc.type = 'sine'; osc.frequency.value = 880;
          const t = ctx.currentTime + delay / 1000;
          gain.gain.setValueAtTime(0.4, t);
          gain.gain.exponentialRampToValueAtTime(0.001, t + 0.3);
          osc.start(t); osc.stop(t + 0.35);
        });
      } catch (_) {}
    },
  };

  /* ========================================================================
     8) مولّد الكلمات العشوائية
     ======================================================================== */
  const WordGenerator = {
    wordBank: {
      general: [
        'سماء','بحر','جبل','نهر','شمس','قمر','نجم','ريح','مطر','زهرة',
        'شجرة','أرض','طريق','بيت','باب','نافذة','كتاب','قلم','ورقة','فكرة',
        'حلم','أمل','سعادة','وقت','لحظة','ذكرى','صوت','ضوء','ظل','لون',
        'كلمة','قصة','أغنية','صورة','ساعة','رحلة','مسافة','حب','صداقة','ثقة',
        'قوة','حكمة','معرفة','فهم','إبداع','خيال','جمال','حياة','طبيعة','سلام',
      ],
      adjectives: [
        'جميل','كبير','صغير','سريع','بطيء','قديم','جديد','حار','بارد','مشرق',
        'غامق','هادئ','صاخب','لطيف','بعيد','قريب','عالٍ','منخفض','ثقيل','خفيف',
        'شفاف','ناعم','خشن','دافئ','حلو','لذيذ','رائع','مدهش','غريب','واضح',
        'حيوي','أمين','شجاع','كريم','فضولي','نشيط','هادئ','ذكي','طيب','نظيف',
      ],
      verbs: [
        'كتب','قرأ','سمع','رأى','أكل','شرب','نام','استيقظ','مشى','ركض',
        'تكلّم','صمت','ابتسم','ضحك','بكى','فكّر','تعلّم','علّم','ساعد','بنى',
        'رسم','غنّى','عزف','رقص','سافر','عاد','فتح','أغلق','بدأ','أنهى',
        'حلّ','سأل','أجاب','بحث','وجد','جرّب','نجح','فشل','حاول','أبدع',
      ],
      nature: [
        'شجرة','نخلة','وردة','أقحوان','نهر','بحيرة','بحر','محيط','جبل','تل',
        'واحة','صحراء','غابة','حديقة','حقل','مرج','عشب','حجر','صخرة','رمل',
        'سحابة','مطر','برق','رعد','ثلج','جليد','ضباب','قوس قزح','فراشة','عصفور',
        'نسر','دلفين','أسد','نمر','فيل','زراف','أرنب','ثعلب','ذئب','حوت',
      ],
      food: [
        'تمر','عنب','تفاح','برتقال','مانجو','موز','فراولة','رمان','بطيخ','خوخ',
        'خبز','أرز','عدس','فول','حمص','دجاج','سمك','لحم','بيض','جبن',
        'عسل','زيت','ملح','سكر','شاي','قهوة','عصير','حليب','لبن','كعكة',
        'بقلاوة','كنافة','حلوى','شوكولاتة','مثلجات','كباب','شاورما','فلافل','منسف','بريان',
      ],
    },

    generatedWords: [],

    init() {
      this.outputEl   = $('#gen-output');
      this.categoryEl = $('#gen-category');
      this.countEl    = $('#gen-count');
      this.copyBtn    = $('#gen-copy');
      this.statusEl   = $('#gen-status');
      this.errorEl    = $('#gen-error');
      if (!this.outputEl) return;

      $('#gen-generate')?.addEventListener('click', () => this.generate());
      this.copyBtn?.addEventListener('click', async () => {
        if (!this.generatedWords.length) return;
        const ok = await copyText(this.generatedWords.join('، '));
        setStatus(this.statusEl, ok ? '✓ تم النسخ.' : 'تعذّر النسخ.', ok ? 'ok' : 'error');
      });
    },

    generate() {
      clearError(this.errorEl);
      const count    = parseInt(this.countEl?.value || '8', 10);
      if (isNaN(count) || count < 1 || count > 20) {
        showError(this.errorEl, 'أدخل عددًا بين ١ و٢٠.'); return;
      }
      const category = this.categoryEl?.value || 'general';
      const pool     = this.wordBank[category] ?? this.wordBank.general;
      const shuffled = [...pool].sort(() => Math.random() - 0.5);
      this.generatedWords = shuffled.slice(0, Math.min(count, pool.length));

      this.outputEl.innerHTML = '';
      this.generatedWords.forEach((word, i) => {
        const chip = el('span', 'chip', word);
        chip.style.animationDelay = `${i * 45}ms`;
        this.outputEl.appendChild(chip);
      });

      if (this.copyBtn) this.copyBtn.disabled = false;
    },
  };

  /* ========================================================================
     9) مولد كلمات المرور
     ======================================================================== */
  const PasswordGenerator = {
    hidden: true,
    password: '',

    chars: {
      upper:     'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
      lower:     'abcdefghijklmnopqrstuvwxyz',
      nums:      '0123456789',
      syms:      '!@#$%^&*()-_=+[]{}|;:,.<>?',
      ambiguous: /[0O1lI]/g,
    },

    init() {
      this.widget     = $('#passgen-widget');
      if (!this.widget) return;
      this.outputEl   = $('#pass-output');
      this.fillEl     = $('#strength-fill');
      this.labelEl    = $('#strength-label');
      this.lengthEl   = $('#pass-length');
      this.lengthVal  = $('#pass-length-val');
      this.statusEl   = $('#pass-status');
      this.errorEl    = $('#pass-error');

      this.lengthEl?.addEventListener('input', () => {
        if (this.lengthVal) this.lengthVal.textContent = this.lengthEl.value;
        if (this.password) this.generate();
      });

      $('#pass-generate')?.addEventListener('click', () => this.generate());
      $('#pass-toggle-view')?.addEventListener('click', () => this.toggleView());

      const copyFn = async () => {
        if (!this.password) { showError(this.errorEl, 'ولِّد كلمة مرور أولًا.'); return; }
        const ok = await copyText(this.password);
        setStatus(this.statusEl, ok ? '✓ تم النسخ.' : 'تعذّر النسخ.', ok ? 'ok' : 'error');
      };
      $('#pass-copy')?.addEventListener('click', copyFn);
      $('#pass-copy-2')?.addEventListener('click', copyFn);

      this.generate();
    },

    generate() {
      clearError(this.errorEl);
      const len  = parseInt(this.lengthEl?.value || '16', 10);
      const useU = $('#opt-upper')?.checked;
      const useL = $('#opt-lower')?.checked;
      const useN = $('#opt-nums')?.checked;
      const useS = $('#opt-syms')?.checked;
      const noAm = $('#opt-ambiguous')?.checked;

      if (!useU && !useL && !useN && !useS) {
        showError(this.errorEl, 'اختر نوعًا واحدًا على الأقل.'); return;
      }

      let pool = '';
      if (useU) pool += this.chars.upper;
      if (useL) pool += this.chars.lower;
      if (useN) pool += this.chars.nums;
      if (useS) pool += this.chars.syms;
      if (noAm) pool = pool.replace(this.chars.ambiguous, '');
      if (!pool.length) { showError(this.errorEl, 'لا يوجد حروف متاحة بعد الاستبعاد.'); return; }

      /* توليد باستخدام crypto عند الإمكان */
      let result = '';
      const arr = new Uint32Array(len);
      if (window.crypto?.getRandomValues) {
        window.crypto.getRandomValues(arr);
        for (let i = 0; i < len; i++) result += pool[arr[i] % pool.length];
      } else {
        for (let i = 0; i < len; i++) result += pool[Math.floor(Math.random() * pool.length)];
      }

      /* ضمان وجود كل نوع مختار */
      const required = [];
      if (useU) required.push(this.chars.upper.replace(noAm ? this.chars.ambiguous : /x^/, ''));
      if (useL) required.push(this.chars.lower.replace(noAm ? this.chars.ambiguous : /x^/, ''));
      if (useN) required.push(this.chars.nums.replace(noAm ? this.chars.ambiguous : /x^/, ''));
      if (useS) required.push(this.chars.syms);

      const resArr = result.split('');
      required.forEach((pool2, i) => {
        if (pool2.length) resArr[i] = pool2[Math.floor(Math.random() * pool2.length)];
      });
      /* خلط الناتج */
      for (let i = resArr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [resArr[i], resArr[j]] = [resArr[j], resArr[i]];
      }
      this.password = resArr.join('');
      this.hidden = false;

      this.renderOutput();
      this.calcStrength(this.password, useU, useL, useN, useS);
    },

    toggleView() {
      this.hidden = !this.hidden;
      this.renderOutput();
    },

    renderOutput() {
      if (!this.outputEl) return;
      if (this.hidden) {
        this.outputEl.textContent = '•'.repeat(this.password.length);
        this.outputEl.dataset.hidden = 'true';
      } else {
        this.outputEl.textContent = this.password;
        this.outputEl.dataset.hidden = 'false';
      }
    },

    calcStrength(pw, u, l, n, s) {
      let score = 0;
      if (pw.length >= 8)  score++;
      if (pw.length >= 12) score++;
      if (pw.length >= 20) score++;
      if (u && /[A-Z]/.test(pw)) score++;
      if (l && /[a-z]/.test(pw)) score++;
      if (n && /[0-9]/.test(pw)) score++;
      if (s && /[^A-Za-z0-9]/.test(pw)) score++;

      const levels = ['', 'weak', 'weak', 'fair', 'fair', 'good', 'good', 'strong'];
      const labels = { weak: 'ضعيفة', fair: 'مقبولة', good: 'جيدة', strong: 'قوية جداً' };
      const level  = levels[Math.min(score, 7)] || 'weak';
      if (this.fillEl)  { this.fillEl.dataset.strength = level; }
      if (this.labelEl) { this.labelEl.textContent = labels[level] || '—'; }
    },
  };

  /* ========================================================================
     10) محول الألوان
     ======================================================================== */
  const ColorConverter = {
    r: 15, g: 118, b: 110,

    init() {
      this.widget = $('#color-widget');
      if (!this.widget) return;
      this.picker  = $('#color-picker');
      this.preview = $('#color-preview');
      this.hexEl   = $('#color-hex');
      this.rgbEl   = $('#color-rgb');
      this.hslEl   = $('#color-hsl');
      this.sliderR = $('#slider-r');
      this.sliderG = $('#slider-g');
      this.sliderB = $('#slider-b');
      this.valR    = $('#val-r');
      this.valG    = $('#val-g');
      this.valB    = $('#val-b');
      this.statusEl= $('#color-status');

      this.picker?.addEventListener('input', () => {
        const hex = this.picker.value;
        this.r = parseInt(hex.slice(1,3),16);
        this.g = parseInt(hex.slice(3,5),16);
        this.b = parseInt(hex.slice(5,7),16);
        this.renderAll();
      });

      this.hexEl?.addEventListener('change', () => {
        const hex = this.hexEl.value.trim();
        if (/^#[0-9a-fA-F]{6}$/.test(hex)) {
          this.r = parseInt(hex.slice(1,3),16);
          this.g = parseInt(hex.slice(3,5),16);
          this.b = parseInt(hex.slice(5,7),16);
          this.renderAll();
        }
      });

      [['slider-r','r'],['slider-g','g'],['slider-b','b']].forEach(([id, ch]) => {
        $(`#${id}`)?.addEventListener('input', (e) => {
          this[ch] = parseInt(e.target.value, 10);
          this.renderAll();
        });
      });

      $$('[data-copy]').forEach(btn => {
        btn.addEventListener('click', async () => {
          const src = $(`#${btn.dataset.copy}`);
          if (!src) return;
          const ok = await copyText(src.value);
          setStatus(this.statusEl, ok ? '✓ تم النسخ.' : 'تعذّر النسخ.', ok ? 'ok' : 'error');
        });
      });

      this.renderAll();
    },

    renderAll() {
      const { r, g, b } = this;
      const hex = `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${b.toString(16).padStart(2,'0')}`;
      const [h, s, l] = this.rgbToHsl(r, g, b);

      if (this.picker)  this.picker.value  = hex;
      if (this.preview) this.preview.style.backgroundColor = hex;
      if (this.hexEl)   this.hexEl.value   = hex;
      if (this.rgbEl)   this.rgbEl.value   = `rgb(${r}, ${g}, ${b})`;
      if (this.hslEl)   this.hslEl.value   = `hsl(${h}, ${s}%, ${l}%)`;

      if (this.sliderR) this.sliderR.value = r;
      if (this.sliderG) this.sliderG.value = g;
      if (this.sliderB) this.sliderB.value = b;
      if (this.valR)    this.valR.textContent = r;
      if (this.valG)    this.valG.textContent = g;
      if (this.valB)    this.valB.textContent = b;
    },

    rgbToHsl(r, g, b) {
      r /= 255; g /= 255; b /= 255;
      const max = Math.max(r,g,b), min = Math.min(r,g,b);
      let h, s, l = (max + min) / 2;
      if (max === min) { h = s = 0; }
      else {
        const d = max - min;
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min);
        switch (max) {
          case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break;
          case g: h = ((b - r) / d + 2) / 6; break;
          default: h = ((r - g) / d + 4) / 6;
        }
      }
      return [Math.round(h*360), Math.round(s*100), Math.round(l*100)];
    },
  };

  /* ========================================================================
     11) محول الوحدات
     ======================================================================== */
  const UnitConverter = {
    category: 'length',

    units: {
      length: [
        { id:'m',   label:'متر (m)',          toBase: v=>v,              fromBase: v=>v },
        { id:'km',  label:'كيلومتر (km)',      toBase: v=>v*1000,         fromBase: v=>v/1000 },
        { id:'cm',  label:'سنتيمتر (cm)',      toBase: v=>v/100,          fromBase: v=>v*100 },
        { id:'mm',  label:'مليمتر (mm)',       toBase: v=>v/1000,         fromBase: v=>v*1000 },
        { id:'mi',  label:'ميل (mi)',          toBase: v=>v*1609.344,     fromBase: v=>v/1609.344 },
        { id:'yd',  label:'ياردة (yd)',        toBase: v=>v*0.9144,       fromBase: v=>v/0.9144 },
        { id:'ft',  label:'قدم (ft)',          toBase: v=>v*0.3048,       fromBase: v=>v/0.3048 },
        { id:'in',  label:'بوصة (in)',         toBase: v=>v*0.0254,       fromBase: v=>v/0.0254 },
      ],
      weight: [
        { id:'kg',  label:'كيلوجرام (kg)',     toBase: v=>v,              fromBase: v=>v },
        { id:'g',   label:'جرام (g)',          toBase: v=>v/1000,         fromBase: v=>v*1000 },
        { id:'mg',  label:'ملليجرام (mg)',     toBase: v=>v/1e6,          fromBase: v=>v*1e6 },
        { id:'t',   label:'طن متري (t)',       toBase: v=>v*1000,         fromBase: v=>v/1000 },
        { id:'lb',  label:'رطل (lb)',          toBase: v=>v*0.453592,     fromBase: v=>v/0.453592 },
        { id:'oz',  label:'أونصة (oz)',        toBase: v=>v*0.0283495,    fromBase: v=>v/0.0283495 },
      ],
      temp: [
        { id:'c',   label:'مئوية (°C)',        toBase: v=>v,              fromBase: v=>v },
        { id:'f',   label:'فهرنهايت (°F)',     toBase: v=>(v-32)*5/9,    fromBase: v=>v*9/5+32 },
        { id:'k',   label:'كلفن (K)',          toBase: v=>v-273.15,       fromBase: v=>v+273.15 },
      ],
      area: [
        { id:'m2',  label:'متر مربع (m²)',     toBase: v=>v,              fromBase: v=>v },
        { id:'km2', label:'كيلومتر مربع (km²)',toBase: v=>v*1e6,          fromBase: v=>v/1e6 },
        { id:'cm2', label:'سنتيمتر مربع (cm²)',toBase: v=>v/10000,        fromBase: v=>v*10000 },
        { id:'ha',  label:'هكتار (ha)',        toBase: v=>v*10000,        fromBase: v=>v/10000 },
        { id:'ac',  label:'فدان (ac)',         toBase: v=>v*4046.86,      fromBase: v=>v/4046.86 },
        { id:'ft2', label:'قدم مربع (ft²)',    toBase: v=>v*0.092903,     fromBase: v=>v/0.092903 },
        { id:'in2', label:'بوصة مربع (in²)',   toBase: v=>v*0.00064516,   fromBase: v=>v/0.00064516 },
      ],
    },

    init() {
      this.widget   = $('#unit-widget');
      if (!this.widget) return;
      this.fromVal  = $('#unit-from-val');
      this.fromSel  = $('#unit-from');
      this.toSel    = $('#unit-to');
      this.resultVal= $('#unit-result-val');
      this.resultLbl= $('#unit-result-label');
      this.statusEl = $('#unit-status');

      $$('[data-cat]').forEach(btn => {
        btn.addEventListener('click', () => {
          $$('[data-cat]').forEach(b => b.classList.remove('tab-btn--active'));
          btn.classList.add('tab-btn--active');
          this.category = btn.dataset.cat;
          this.buildSelects();
          this.convert();
        });
      });

      this.fromVal?.addEventListener('input', () => this.convert());
      this.fromSel?.addEventListener('change', () => this.convert());
      this.toSel?.addEventListener('change',   () => this.convert());

      $('#unit-swap')?.addEventListener('click', () => {
        const tmp = this.fromSel.value;
        this.fromSel.value = this.toSel.value;
        this.toSel.value   = tmp;
        this.convert();
      });

      $('#unit-copy')?.addEventListener('click', async () => {
        const txt = this.resultVal?.textContent;
        if (!txt || txt === '—') return;
        const ok = await copyText(txt);
        setStatus(this.statusEl, ok ? '✓ تم النسخ.' : 'تعذّر النسخ.', ok ? 'ok' : 'error');
      });

      this.buildSelects();
      this.convert();
    },

    buildSelects() {
      const list = this.units[this.category] || [];
      [this.fromSel, this.toSel].forEach((sel, i) => {
        if (!sel) return;
        sel.innerHTML = '';
        list.forEach(u => {
          const opt = document.createElement('option');
          opt.value = u.id; opt.textContent = u.label;
          sel.appendChild(opt);
        });
        if (i === 1 && list.length > 1) sel.selectedIndex = 1;
      });
    },

    convert() {
      const list  = this.units[this.category] || [];
      const fromU = list.find(u => u.id === this.fromSel?.value);
      const toU   = list.find(u => u.id === this.toSel?.value);
      const val   = parseFloat(this.fromVal?.value);

      if (!fromU || !toU || isNaN(val)) {
        if (this.resultVal) this.resultVal.textContent = '—';
        return;
      }

      const base   = fromU.toBase(val);
      const result = toU.fromBase(base);
      const nice   = Number.isFinite(result)
        ? (Math.abs(result) < 1e-6 && result !== 0
            ? result.toExponential(4)
            : parseFloat(result.toPrecision(7)))
        : '—';

      if (this.resultVal) this.resultVal.textContent = String(nice);
      if (this.resultLbl) this.resultLbl.textContent = toU.label;
    },
  };

  /* ========================================================================
     12) المفكرة الشخصية
     ======================================================================== */
  const Notepad = {
    STORAGE_KEY: 'toolbox_notepad_v1',
    saveTimer: null,

    init() {
      this.widget   = $('#notepad-widget');
      if (!this.widget) return;
      this.input    = $('#notepad-input');
      this.saveEl   = $('#notepad-save-status');
      this.wordsEl  = $('#np-words');
      this.charsEl  = $('#np-chars');
      this.linesEl  = $('#np-lines');

      /* استعادة المحفوظ */
      try {
        const saved = localStorage.getItem(this.STORAGE_KEY);
        if (saved && this.input) this.input.value = saved;
      } catch(_) {}

      this.input?.addEventListener('input', () => {
        this.updateStats();
        this.scheduleSave();
      });

      $('#notepad-copy')?.addEventListener('click', async () => {
        const ok = await copyText(this.input?.value || '');
        if (this.saveEl) this.saveEl.textContent = ok ? '✓ تم النسخ' : 'تعذّر النسخ';
      });

      $('#notepad-download')?.addEventListener('click', () => {
        const content = this.input?.value || '';
        const blob = new Blob([content], {type:'text/plain;charset=utf-8'});
        const url  = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = 'مفكرتي.txt'; a.click();
        URL.revokeObjectURL(url);
      });

      $('#notepad-clear')?.addEventListener('click', () => {
        if (!confirm('هل تريد مسح كل المحتوى؟')) return;
        if (this.input) this.input.value = '';
        try { localStorage.removeItem(this.STORAGE_KEY); } catch(_) {}
        this.updateStats();
        if (this.saveEl) this.saveEl.textContent = 'تم المسح';
      });

      this.updateStats();
    },

    scheduleSave() {
      if (this.saveEl) this.saveEl.textContent = 'جاري الحفظ…';
      clearTimeout(this.saveTimer);
      this.saveTimer = setTimeout(() => {
        try {
          localStorage.setItem(this.STORAGE_KEY, this.input?.value || '');
          if (this.saveEl) this.saveEl.textContent = '✓ تم الحفظ';
        } catch(_) {
          if (this.saveEl) this.saveEl.textContent = 'تعذّر الحفظ';
        }
      }, 800);
    },

    updateStats() {
      const text = this.input?.value || '';
      const words = text.trim() ? text.trim().split(/\s+/).length : 0;
      const lines = text ? text.split('\n').length : 0;
      if (this.wordsEl) this.wordsEl.textContent = `${words} كلمة`;
      if (this.charsEl) this.charsEl.textContent = `${text.length} حرف`;
      if (this.linesEl) this.linesEl.textContent = `${lines} سطر`;
    },
  };

  /* ========================================================================
     13) حاسب العمر
     ======================================================================== */
  const AgeCalculator = {
    init() {
      this.widget     = $('#age-widget');
      if (!this.widget) return;
      this.birthEl    = $('#age-birthdate');
      this.refEl      = $('#age-refdate');
      this.resultsEl  = $('#age-results');
      this.errorEl    = $('#age-error');

      /* تعيين تاريخ اليوم كقيمة افتراضية لحقل المرجع */
      const today = new Date();
      const todayStr = today.toISOString().split('T')[0];
      if (this.refEl) this.refEl.value = todayStr;
      /* أقصى تاريخ للميلاد = اليوم */
      if (this.birthEl) this.birthEl.max = todayStr;

      $('#age-calculate')?.addEventListener('click', () => this.calculate());
      this.birthEl?.addEventListener('change', () => {
        if (this.birthEl.value) this.calculate();
      });
    },

    calculate() {
      clearError(this.errorEl);
      const birthStr = this.birthEl?.value;
      if (!birthStr) { showError(this.errorEl, 'أدخل تاريخ الميلاد.'); return; }

      const refStr = this.refEl?.value || new Date().toISOString().split('T')[0];
      const birth  = new Date(birthStr);
      const ref    = new Date(refStr);

      if (isNaN(birth.getTime())) { showError(this.errorEl, 'تاريخ الميلاد غير صالح.'); return; }
      if (birth > ref)            { showError(this.errorEl, 'تاريخ الميلاد يجب أن يكون قبل تاريخ المرجع.'); return; }

      let years  = ref.getFullYear() - birth.getFullYear();
      let months = ref.getMonth()    - birth.getMonth();
      let days   = ref.getDate()     - birth.getDate();

      if (days   < 0) { months--; const prev = new Date(ref.getFullYear(), ref.getMonth(), 0); days += prev.getDate(); }
      if (months < 0) { years--; months += 12; }

      const diffMs     = ref - birth;
      const totalDays  = Math.floor(diffMs / 86400000);
      const totalWeeks = Math.floor(totalDays / 7);
      const totalHours = totalDays * 24;

      $('#age-years').textContent      = years.toLocaleString('ar-SA');
      $('#age-months').textContent     = months.toLocaleString('ar-SA');
      $('#age-days').textContent       = days.toLocaleString('ar-SA');
      $('#age-total-days').textContent = totalDays.toLocaleString('ar-SA');
      $('#age-weeks').textContent      = totalWeeks.toLocaleString('ar-SA');
      $('#age-hours').textContent      = totalHours.toLocaleString('ar-SA');

      /* عيد الميلاد القادم */
      const info = $('#age-birthday-info');
      if (info) {
        const nextBD = new Date(ref.getFullYear(), birth.getMonth(), birth.getDate());
        if (nextBD <= ref) nextBD.setFullYear(nextBD.getFullYear() + 1);
        const daysLeft = Math.ceil((nextBD - ref) / 86400000);
        info.textContent = daysLeft === 0
          ? '🎉 عيد ميلاد سعيد! اليوم هو يومك!'
          : `🎂 عيد ميلادك القادم بعد ${daysLeft.toLocaleString('ar-SA')} يوم`;
      }

      if (this.resultsEl) this.resultsEl.hidden = false;
    },
  };

  /* ========================================================================
     14) منسّق ومدقّق JSON
     ======================================================================== */
  const JsonFormatter = {
    init() {
      this.widget   = $('#json-widget');
      if (!this.widget) return;
      this.input    = $('#json-input');
      this.output   = $('#json-output');
      this.indent   = $('#json-indent');
      this.errorEl  = $('#json-error');
      this.statusEl = $('#json-status');

      $('#json-format')?.addEventListener('click', () => this.transform('format'));
      $('#json-minify')?.addEventListener('click', () => this.transform('minify'));
      $('#json-copy')?.addEventListener('click', () => this.copy());
      $('#json-clear')?.addEventListener('click', () => this.clear());
      this.input?.addEventListener('keydown', (event) => {
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
          event.preventDefault();
          this.transform('format');
        }
      });
    },

    transform(mode) {
      clearError(this.errorEl);
      const source = this.input?.value.trim() || '';
      if (!source) {
        showError(this.errorEl, 'ألصق أو اكتب JSON أولًا.');
        return;
      }
      try {
        const parsed = JSON.parse(source);
        const indent = this.indent?.value === '1' ? '\t' : Number(this.indent?.value || 2);
        if (this.output) this.output.value = mode === 'minify'
          ? JSON.stringify(parsed)
          : JSON.stringify(parsed, null, indent);
        setStatus(this.statusEl, mode === 'minify' ? '✓ JSON صالح وتم تصغيره.' : '✓ JSON صالح وتم تنسيقه.');
      } catch (_) {
        showError(this.errorEl, 'JSON غير صالح. تحقّق من علامات الاقتباس والفواصل والأقواس.');
      }
    },

    async copy() {
      const result = this.output?.value || '';
      if (!result) { setStatus(this.statusEl, 'لا توجد نتيجة لنسخها.', 'error'); return; }
      const ok = await copyText(result);
      setStatus(this.statusEl, ok ? '✓ تم النسخ.' : 'تعذّر النسخ.', ok ? 'ok' : 'error');
    },

    clear() {
      if (this.input) this.input.value = '';
      if (this.output) this.output.value = '';
      clearError(this.errorEl);
      setStatus(this.statusEl, '', 'ok', 0);
      this.input?.focus();
    },
  };

  /* ========================================================================
     15) الاختيار العشوائي من قائمة
     ======================================================================== */
  const RandomPicker = {
    init() {
      this.widget   = $('#picker-widget');
      if (!this.widget) return;
      this.input    = $('#picker-input');
      this.removeEl = $('#picker-remove');
      this.output   = $('#picker-output');
      this.countEl  = $('#picker-count');
      this.statusEl = $('#picker-status');

      $('#picker-choose')?.addEventListener('click', () => this.choose());
      $('#picker-copy')?.addEventListener('click', () => this.copy());
      $('#picker-clear')?.addEventListener('click', () => this.clear());
      this.input?.addEventListener('input', () => this.updateCount());
      this.updateCount();
    },

    entries() {
      return (this.input?.value || '').split(/\r?\n/).map(value => value.trim()).filter(Boolean);
    },

    randomIndex(max) {
      if (window.crypto?.getRandomValues) {
        const limit = Math.floor(0x100000000 / max) * max;
        const value = new Uint32Array(1);
        do { window.crypto.getRandomValues(value); } while (value[0] >= limit);
        return value[0] % max;
      }
      return Math.floor(Math.random() * max);
    },

    choose() {
      const options = this.entries();
      if (!options.length) {
        setStatus(this.statusEl, 'أضف خيارًا واحدًا على الأقل.', 'error');
        return;
      }
      const winner = options[this.randomIndex(options.length)];
      if (this.output) this.output.textContent = winner;
      if (this.removeEl?.checked && this.input) {
        const lines = this.input.value.split(/\r?\n/);
        const position = lines.findIndex(line => line.trim() === winner);
        if (position !== -1) this.input.value = lines.filter((_, index) => index !== position).join('\n');
      }
      this.updateCount();
      setStatus(this.statusEl, '✓ تم الاختيار عشوائيًا.');
    },

    updateCount() {
      const count = this.entries().length;
      if (this.countEl) this.countEl.textContent = count
        ? `${count.toLocaleString('ar-SA')} خيار${count === 1 ? '' : 'ات'} متاحة`
        : 'أضف خياراتك للبدء';
    },

    async copy() {
      const winner = this.output?.textContent || '';
      if (!winner || winner === '—') { setStatus(this.statusEl, 'اختر نتيجة أولًا.', 'error'); return; }
      const ok = await copyText(winner);
      setStatus(this.statusEl, ok ? '✓ تم النسخ.' : 'تعذّر النسخ.', ok ? 'ok' : 'error');
    },

    clear() {
      if (this.input) this.input.value = '';
      if (this.output) this.output.textContent = '—';
      this.updateCount();
      setStatus(this.statusEl, '', 'ok', 0);
      this.input?.focus();
    },
  };

  /* ========================================================================
     16) ساعة الإيقاف
     ======================================================================== */
  const Stopwatch = {
    state: 'idle',
    elapsedMs: 0,
    startedAt: 0,
    rafId: null,
    laps: [],

    init() {
      this.widget   = $('#stopwatch-widget');
      if (!this.widget) return;
      this.display  = $('#stopwatch-display');
      this.lapsEl   = $('#stopwatch-laps');
      this.emptyEl  = $('#stopwatch-empty');
      this.startBtn = $('#stopwatch-start');
      this.pauseBtn = $('#stopwatch-pause');
      this.lapBtn   = $('#stopwatch-lap');
      this.resetBtn = $('#stopwatch-reset');

      this.startBtn?.addEventListener('click', () => this.start());
      this.pauseBtn?.addEventListener('click', () => this.pause());
      this.lapBtn?.addEventListener('click', () => this.addLap());
      this.resetBtn?.addEventListener('click', () => this.reset());
      this.render();
      this.updateButtons();
    },

    start() {
      if (this.state === 'running') return;
      this.startedAt = performance.now() - this.elapsedMs;
      this.state = 'running';
      this.updateButtons();
      this.tick();
    },

    pause() {
      if (this.state !== 'running') return;
      this.elapsedMs = performance.now() - this.startedAt;
      this.state = 'paused';
      cancelAnimationFrame(this.rafId);
      this.render();
      this.updateButtons();
    },

    reset() {
      cancelAnimationFrame(this.rafId);
      this.state = 'idle';
      this.elapsedMs = 0;
      this.laps = [];
      this.render();
      this.renderLaps();
      this.updateButtons();
    },

    tick() {
      if (this.state !== 'running') return;
      this.elapsedMs = performance.now() - this.startedAt;
      this.render();
      this.rafId = requestAnimationFrame(() => this.tick());
    },

    addLap() {
      if (this.state !== 'running') return;
      const previous = this.laps.length ? this.laps[this.laps.length - 1].total : 0;
      this.laps.push({ total: this.elapsedMs, duration: this.elapsedMs - previous });
      this.renderLaps();
    },

    format(ms) {
      const totalCentiseconds = Math.floor(ms / 10);
      const cs = totalCentiseconds % 100;
      const totalSeconds = Math.floor(totalCentiseconds / 100);
      const seconds = totalSeconds % 60;
      const minutes = Math.floor(totalSeconds / 60) % 60;
      const hours = Math.floor(totalSeconds / 3600);
      return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}.${String(cs).padStart(2, '0')}`;
    },

    render() {
      const value = this.format(this.elapsedMs);
      if (this.display) {
        this.display.textContent = value;
        this.display.dateTime = `PT${Math.floor(this.elapsedMs / 1000)}S`;
      }
    },

    renderLaps() {
      if (!this.lapsEl) return;
      this.lapsEl.replaceChildren();
      this.laps.slice().reverse().forEach((lap, index) => {
        const item = el('li', 'laps__item');
        const number = el('span', '', `#${this.laps.length - index}`);
        const total = el('span', '', this.format(lap.total));
        const duration = el('span', '', this.format(lap.duration));
        item.append(number, total, duration);
        this.lapsEl.appendChild(item);
      });
      if (this.emptyEl) this.emptyEl.hidden = this.laps.length > 0;
    },

    updateButtons() {
      const isRunning = this.state === 'running';
      const isIdle = this.state === 'idle';
      if (this.startBtn) {
        this.startBtn.disabled = isRunning;
        this.startBtn.textContent = this.state === 'paused' ? '▶ استئناف' : '▶ تشغيل';
      }
      if (this.pauseBtn) this.pauseBtn.disabled = !isRunning;
      if (this.lapBtn) this.lapBtn.disabled = !isRunning;
      if (this.resetBtn) this.resetBtn.disabled = isIdle;
    },
  };

  /* ========================================================================
     14) التهيئة — اكتشاف الصفحة الحالية وتشغيل الأداة المناسبة
     ======================================================================== */
  document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initCommon();

    const page = location.pathname.split('/').pop() || 'index.html';

    if (page === 'calculator.html')        Calculator.init();
    if (page === 'case-converter.html')    CaseConverter.init();
    if (page === 'text-counter.html')      TextCounter.init();
    if (page === 'timer.html')             Timer.init();
    if (page === 'word-generator.html')    WordGenerator.init();
    if (page === 'password-generator.html') PasswordGenerator.init();
    if (page === 'color-converter.html')   ColorConverter.init();
    if (page === 'unit-converter.html')    UnitConverter.init();
    if (page === 'notepad.html')           Notepad.init();
    if (page === 'age-calculator.html')    AgeCalculator.init();
    if (page === 'json-formatter.html')    JsonFormatter.init();
    if (page === 'random-picker.html')     RandomPicker.init();
    if (page === 'stopwatch.html')          Stopwatch.init();
    /* index.html — لا تحتاج تهيئة أداة */
  });

})();
