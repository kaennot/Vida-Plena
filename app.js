(() => {
  const root = document.documentElement;
  let saved = '100';
  try { saved = localStorage.getItem('vida-plena-font') || '100'; } catch(e) {}
  const value = Number(saved);
  let current = [100,112,125,138].includes(value) ? value : 100;
  const apply = () => { root.style.fontSize = current + '%'; try { localStorage.setItem('vida-plena-font', String(current)); } catch(e) {} };
  apply();
  document.getElementById('font-plus')?.addEventListener('click', () => { current = Math.min(138, current === 100 ? 112 : current === 112 ? 125 : 138); apply(); });
  document.getElementById('font-minus')?.addEventListener('click', () => { current = current === 138 ? 125 : current === 125 ? 112 : 100; apply(); });
  const menu = document.getElementById('menu-button');
  const nav = document.getElementById('nav');
  menu?.addEventListener('click', () => {
    const opened = nav.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(opened));
  });
  nav?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
    nav.classList.remove('open'); menu?.setAttribute('aria-expanded','false');
  }));
  const textarea = document.getElementById('mensaje');
  const counter = document.getElementById('message-counter');
  textarea?.addEventListener('input', () => { if(counter) counter.textContent = `${textarea.value.length} de 2500 caracteres`; });
  const form = document.getElementById('contact-form');
  form?.addEventListener('submit', () => {
    if(!form.checkValidity()) return;
    const button = form.querySelector('[type="submit"]');
    if(button) { button.textContent = 'Guardando mensaje…'; button.disabled = true; }
  });
})();
