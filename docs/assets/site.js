(() => {
  'use strict';
  const input = document.querySelector('#search');
  if (input) {
    const cards = [...document.querySelectorAll('.card')];
    const buttons = [...document.querySelectorAll('[data-filter]')];
    let category = '';
    const normalize = s => s.toLocaleLowerCase('ru').replaceAll('ё', 'е');
    const update = () => {
      const words = normalize(input.value).trim().split(/\s+/).filter(Boolean);
      let count = 0;
      cards.forEach(card => {
        const matches = (!category || card.dataset.category === category) && words.every(word => normalize(card.dataset.search).includes(word));
        card.hidden = !matches;
        if (matches) count++;
      });
      document.querySelector('#result-count').textContent = `Материалов: ${count} из ${cards.length}`;
      document.querySelector('#empty').hidden = count > 0;
      document.querySelector('#clear-search').hidden = input.value.length === 0;
    };
    input.value = new URLSearchParams(location.search).get('q') || '';
    input.addEventListener('input', update);
    document.querySelector('#clear-search').addEventListener('click', () => { input.value = ''; update(); input.focus(); });
    buttons.forEach(button => button.addEventListener('click', () => {
      category = button.dataset.filter;
      buttons.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
      update();
    }));
    document.querySelector('#reset-filters').addEventListener('click', () => { input.value=''; buttons[0].click(); input.focus(); });
    update();
  }
  document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
    const text = document.querySelector(button.dataset.copy).textContent;
    try {
      await navigator.clipboard.writeText(text);
      button.textContent = 'Запрос скопирован';
    } catch {
      const range = document.createRange(); range.selectNodeContents(document.querySelector(button.dataset.copy));
      const selection = window.getSelection(); selection.removeAllRanges(); selection.addRange(range);
      button.textContent = 'Текст выделен — скопируйте вручную';
    }
  }));
})();
