const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 800 } });
  
  await page.goto('http://localhost:8080');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/root/.openclaw/workspace/obsidian-sync-local/site/screenshot-index.png', fullPage: false });
  
  await page.goto('http://localhost:8080/digest-2026-06-16.html');
  await page.waitForTimeout(2000);
  await page.screenshot({ path: '/root/.openclaw/workspace/obsidian-sync-local/site/screenshot-digest.png', fullPage: false });
  
  await browser.close();
  console.log('Screenshots saved');
})();