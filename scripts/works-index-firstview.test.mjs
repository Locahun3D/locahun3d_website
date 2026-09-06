import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { createReadStream, statSync } from 'node:fs';
import { resolve, sep } from 'node:path';
import test, { after, before } from 'node:test';
import { chromium } from 'playwright';

const root = resolve(import.meta.dirname, '..');
let server;
let browser;
let origin;

before(async () => {
  server = createServer((request, response) => {
    const pathname = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const file = resolve(root, `.${pathname}`);
    if (!file.startsWith(`${root}${sep}`) || !statSync(file, { throwIfNoEntry: false })?.isFile()) {
      response.writeHead(404).end();
      return;
    }
    response.setHeader('content-type', file.endsWith('.html') ? 'text/html; charset=utf-8' : 'application/octet-stream');
    createReadStream(file).pipe(response);
  });
  await new Promise(resolveReady => server.listen(0, '127.0.0.1', resolveReady));
  origin = `http://127.0.0.1:${server.address().port}`;
  browser = await chromium.launch({ channel: 'chrome', headless: true });
});

after(async () => {
  await browser?.close();
  await new Promise(resolveClosed => server?.close(resolveClosed));
});

for (const path of ['/works/index.html', '/en/works/index.html']) {
  test(`${path} keeps the primary work and first technical article in the 1440x900 opening view`, async () => {
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    await page.goto(`${origin}${path}`, { waitUntil: 'domcontentloaded' });
    const layout = await page.evaluate(() => {
      const rect = selector => document.querySelector(selector)?.getBoundingClientRect().toJSON();
      return {
        liveWork: rect('#worksGrid .card:not(.ph)'),
        firstArticle: rect('#blogGrid .card:not(.ph)'),
        workAccent: getComputedStyle(document.querySelector('#worksGrid .card:not(.ph) .cm')).color,
        techAccent: getComputedStyle(document.querySelector('#blog .chip.active')).backgroundColor,
        placeholders: [...document.querySelectorAll('#worksGrid .card.ph')].map(card => card.getBoundingClientRect().toJSON()),
        overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      };
    });
    assert.ok(layout.liveWork, 'primary work card must render');
    assert.ok(layout.firstArticle, 'first technical article must render');
    assert.ok(layout.liveWork.bottom <= 900, `work card bottom ${layout.liveWork.bottom} exceeds viewport`);
    assert.ok(layout.firstArticle.bottom <= 900, `article card bottom ${layout.firstArticle.bottom} exceeds viewport`);
    assert.equal(layout.workAccent, 'rgb(255, 180, 84)');
    assert.equal(layout.techAccent, 'rgb(30, 160, 196)');
    assert.equal(layout.placeholders.length, 2);
    assert.ok(layout.placeholders.every(card => card.height < layout.liveWork.height * 0.5), 'coming-soon works must remain visually secondary');
    assert.equal(layout.overflow, 0);
    await page.close();
  });

  for (const width of [820, 390]) {
    test(`${path} has no horizontal overflow at ${width}px`, async () => {
      const page = await browser.newPage({ viewport: { width, height: 900 } });
      await page.goto(`${origin}${path}`, { waitUntil: 'domcontentloaded' });
      const layout = await page.evaluate(() => {
        const hero = document.querySelector('.hero').getBoundingClientRect();
        const live = document.querySelector('#worksGrid .card:not(.ph)').getBoundingClientRect();
        const placeholders = [...document.querySelectorAll('#worksGrid .card.ph')].map(card => {
          const rect = card.getBoundingClientRect();
          return { height: rect.height, width: rect.width };
        });
        return { heroHeight: hero.height, live: { height: live.height, width: live.width }, placeholders, overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth };
      });
      assert.equal(layout.overflow, 0);
      assert.ok(layout.heroHeight <= 150, `hero height ${layout.heroHeight} is too large at ${width}px`);
      const liveArea = layout.live.height * layout.live.width;
      assert.ok(layout.placeholders.every(card => card.height * card.width < liveArea * 0.5), 'coming-soon works must stay secondary');
      await page.close();
    });
  }
}
