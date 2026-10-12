/** Public V2 browser smoke; manual/CI after a verified deployment only.
 * Requires: npm install --no-save playwright@1.56.1 && npx playwright install chromium
 * This script NEVER changes production or compares legacy forecast output.
 */
import { chromium } from 'playwright';

const url = process.argv[2] || 'https://chaselights.app/apps/web-v2/';
const parsed = new URL(url);
if (parsed.protocol !== 'https:' || parsed.hostname !== 'chaselights.app' ||
    parsed.pathname.replace(/\/$/, '') !== '/apps/web-v2') {
  throw new Error('Only canonical ChaseLights V2 public URL is allowed');
}
const browser = await chromium.launch({headless: true});
try {
  for (const width of [390, 1280]) {
    const page = await browser.newPage({viewport: {width, height: 844}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const response = await page.goto(url, {waitUntil: 'networkidle', timeout: 45000});
    if (response?.status() !== 200) throw new Error(`V2 HTTP ${response?.status()} at ${width}px`);
    await page.waitForFunction(
      () => (document.querySelector('#headline')?.textContent || '').trim().length > 0,
      {timeout: 15000}
    );
    const titles = [];
    for (const locale of ['zh-TW', 'en', 'ja']) {
      await page.locator('#language').selectOption(locale);
      const headline = (await page.locator('#headline').textContent() || '').trim();
      const state = (await page.locator('#data-status').textContent() || '').trim();
      if (!headline || !state) throw new Error(`Empty localized content: ${locale} at ${width}px`);
      titles.push(headline);
    }
    if (new Set(titles).size !== 3) throw new Error(`Headline localization not distinct at ${width}px`);
    const dimensions = await page.evaluate(() => ({
      scroll: document.documentElement.scrollWidth,
      client: document.documentElement.clientWidth
    }));
    if (dimensions.scroll > dimensions.client + 2) {
      throw new Error(`Horizontal overflow at ${width}px: ${JSON.stringify(dimensions)}`);
    }
    if (errors.length) throw new Error(`JS errors at ${width}px: ${errors.join('; ')}`);
    console.log(`PASS ${width}px / zh-TW,en,ja / no JS error / no overflow`);
    await page.close();
  }
} finally {
  await browser.close();
}
