from pyppeteer import launch
import asyncio
import nest_asyncio
import pyautogui

nest_asyncio.apply()


# async def hot_key(page,key1,key2):
#     # page.keyboard.press模拟键盘按下某个按键
#     await page.keyboard.down(key1) 
#     await page.keyboard.press(key2) 
#     await page.keyboard.up(key1)


async def main(url,output_pdf,output_html):
    browser = await launch()
    page = await browser.newPage()
    await page.setJavaScriptEnabled(enabled=True)
    await page.goto(url)
    await page.evaluate('''async () => {
                    await new
                Promise((resolve, reject) => {
                    var
                totalHeight = 0;
                var
                distance = 100;
                var
                timer = setInterval(() => {
                    var
                scrollHeight = document.body.scrollHeight;
                window.scrollBy(0, distance);
                totalHeight += distance;

                if (totalHeight >= scrollHeight){
                clearInterval(timer);
                resolve();
                }
                }, 100);
                });
        }''')
    await page.pdf({
        "path": output_pdf, "format": 'A4'})
    
    # 获取页面内容
    content = await page.content()
    # 将内容保存为HTML文件
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write(content)
        
    # pyautogui.hotkey('ctrl', 's')  #键盘ctrl s  保存原始页面
    # await asyncio.sleep(2)
    # pyautogui.press('enter')
    
    await browser.close()
    

if __name__ == '__main__':
    
    url = 'https://mp.weixin.qq.com/s/rFPH3265sMB59ioKKL8aLA'
    output_html = 'test.html'
    output_pdf = 'test.pdf'
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(url,output_pdf,output_html))