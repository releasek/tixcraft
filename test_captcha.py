# ======================================================================
# ============ ibon 驗證碼獨立測試腳本 (最終實戰版) ===============
# ======================================================================
import time
import json
import base64
import random
import sys
import os

# --- 請確保這些套件已經安裝 ---
# pip install selenium undetected-chromedriver ddddocr
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import undetected_chromedriver as uc
import ddddocr

# --- 輔助函式 (已驗證成功) ---
def find_shadow_root_by_internal_selector(driver, wait, internal_css_selector):
    """透過遍歷頁面上所有元素，找到包含特定內部選擇器的 Shadow Root。"""
    try:
        # [智能升級] 直接在JS中判斷 src，減少來回通訊
        js_find_host = f"""
            const allElements = document.querySelectorAll('*');
            for (const element of allElements) {{
                if (element.shadowRoot) {{
                    const img = element.shadowRoot.querySelector('{internal_css_selector}');
                    if (img && img.src.includes('/pic.aspx')) {{
                        return element;
                    }}
                }}
            }}
            return null;
        """
        host_element = wait.until(
            lambda d: d.execute_script(js_find_host),
            message=f"逆向探測超時：找不到內部包含 '{internal_css_selector}' 的 Shadow DOM。"
        )
        return driver.execute_script('return arguments[0].shadowRoot', host_element) if host_element else None
    except Exception:
        return None

# --- [改造後] 最終實戰版 OCR 處理器 ---
def ibon_ocr_captcha_handler(driver, ocr):
    """處理圖片式驗證碼 (逆向探測 + OCR)"""
    wait = WebDriverWait(driver, 10) # 恢復正常等待時間
    print("\n--- INFO: 開始處理圖片式驗證碼 (實戰模式)... ---")
    if not ocr:
        print("ERROR: ddddocr 模組未初始化。")
        return False
        
    try:
        # 1. 使用我們已驗證的智能邏輯，直接找到驗證碼的 Shadow Root
        # 尋找一個內部包含 <img src="/pic.aspx..."> 的 Shadow DOM
        shadow_root = find_shadow_root_by_internal_selector(driver, wait, "img")
        if not shadow_root: 
            print("ERROR: 逆向探測失敗，找不到驗證碼的 Shadow Root。")
            return False
        print("SUCCESS: 成功進入驗證碼的 Shadow DOM！")

        # 2. 提取圖片 Base64 資料
        captcha_image = shadow_root.find_element(By.CSS_SELECTOR, "img") # 裡面只有一張圖
        img_base64_data = driver.execute_async_script("""
            var canvas = document.createElement('canvas');
            var context = canvas.getContext('2d');
            var img = arguments[0];
            if (!img.complete || typeof img.naturalWidth == "undefined" || img.naturalWidth == 0) {
                arguments[arguments.length - 1](null);
                return;
            }
            canvas.height = img.naturalHeight;
            canvas.width = img.naturalWidth;
            context.drawImage(img, 0, 0);
            arguments[arguments.length - 1](canvas.toDataURL('image/png'));
            """, captcha_image)

        if not img_base64_data:
            print("ERROR: 無法獲取驗證碼圖片的 Base64 資料。")
            return False

        # 3. 使用 ddddocr 進行辨識
        img_bytes = base64.b64decode(img_base64_data.split(',')[1])
        ocr_answer = ocr.classification(img_bytes)
        print(f"SUCCESS: OCR 辨識結果: {ocr_answer}")

        # 4. 填寫答案
        answer_input = driver.find_element(By.CSS_SELECTOR, "input[name$='CHK']")
        answer_input.clear()
        answer_input.send_keys(ocr_answer)
        print(f"SUCCESS: 已將 '{ocr_answer}' 自動填入驗證碼。")
        
        return True

    except TimeoutException:
        print("ERROR: 等待驗證碼圖片時超時。")
        return False
    except Exception as e:
        print(f"ERROR: OCR 驗證碼處理失敗: {e}")
        return False

# --- 主執行程式 (改造後，直接執行破解) ---
if __name__ == "__main__":
    target_url = "https://orders.ibon.com.tw/application/UTK02/UTK0202_.aspx?PERFORMANCE_ID=B08SK4AM&GROUP_ID=&PERFORMANCE_PRICE_AREA_ID=B08SKIKH"

    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = uc.Chrome(options=options)
    
    js_to_force_open_shadow_dom = """
    (function() {
      const _attach = Element.prototype.attachShadow;
      Element.prototype.attachShadow = function(init) {
        if(init && init.mode === 'closed'){
          init.mode = 'open';
        }
        return _attach.call(this, init);
      };
    })();
    """
    try:
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": js_to_force_open_shadow_dom}
        )
        print("SUCCESS: 全局破解腳本已設定。")
    except Exception as e:
        print(f"ERROR: 全局腳本注入失敗: {e}")
        driver.quit()
        sys.exit()

    print(f"INFO: 正在導航至目標頁面: {target_url}")
    driver.get(target_url)

    print("\n" + "="*50)
    input(">>>>>> 請在瀏覽器中手動完成「選擇張數」，直到看見驗證碼為止，然後回來這裡按下 Enter 鍵... <<<<<<")
    print("="*50 + "\n")

    # [關鍵步驟] 初始化 OCR 並執行我們的實戰版破解器
    try:
        ocr_instance = ddddocr.DdddOcr(show_ad=False)
        print("INFO: ddddocr 已初始化。")
        
        is_success = ibon_ocr_captcha_handler(driver, ocr_instance)
        
        if is_success:
            print("\n[測試結果]: 破解成功！🎉")
        else:
            print("\n[測試結果]: 破解失敗。請檢查上方的錯誤日誌。")

    except Exception as e:
        print(f"ERROR: 測試過程中發生嚴重錯誤: {e}")
    
    input("\n測試完畢。瀏覽器將保持開啟，以便您檢查。按 Enter 鍵關閉程式。")
    driver.quit()
