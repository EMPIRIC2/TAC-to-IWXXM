"""Selenium UI tests with auth token injection.

Registers a user and seeds sessionStorage token before conversions.
Skips gracefully if Chrome/WebDriver unavailable.
"""
from __future__ import annotations
from gui.app import app as gui_app

import os
import tempfile
import threading
import time
import random
import string
import sys
import pathlib
from pathlib import Path

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

import uvicorn

# Ensure repository root on path
ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


PORT = 8021
BASE_URL = f"http://127.0.0.1:{PORT}"
SAMPLE_METAR = "METAR KJFK 231751Z 18012KT 10SM FEW040 15/07 A3005"
SAMPLE_METAR_2 = "METAR KLAX 231753Z 25008KT 10SM FEW020 18/12 A2992"


@pytest.fixture(scope="session")
def start_server():
    config = uvicorn.Config(gui_app, host="127.0.0.1",
                            port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(50):
        if getattr(server, "started", False):
            break
        time.sleep(0.1)
    yield


@pytest.fixture(scope="session")
def auth_token(start_server) -> str:
    suffix = ''.join(random.choices(
        string.ascii_lowercase + string.digits, k=8))
    reg_payload = {
        "name": "Selenium User",
        "email": f"selenium-{suffix}@example.com",
        "address": "1 Browser Way",
        "username": f"seluser{suffix}",
        "password": "StrongPass123!",
    }
    r = requests.post(f"{BASE_URL}/auth/register", json=reg_payload)
    r.raise_for_status()
    login = requests.post(f"{BASE_URL}/auth/login", json={
        "username": reg_payload["username"], "password": reg_payload["password"]
    })
    login.raise_for_status()
    return login.json()["access_token"]


@pytest.fixture()
def driver(start_server, auth_token):
    if os.getenv("SKIP_SELENIUM"):
        pytest.skip("SKIP_SELENIUM set")
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    try:
        drv = webdriver.Chrome(ChromeDriverManager().install(), options=opts)
    except Exception as e:
        pytest.skip(f"Chrome/WebDriver unavailable: {e}")
    drv.set_window_size(1280, 900)
    drv.get(BASE_URL + "/")
    # Seed sessionStorage token to satisfy auth checks
    drv.execute_script(
        "sessionStorage.setItem('token', arguments[0]);", auth_token)
    drv.refresh()
    yield drv
    drv.quit()


def test_ui_manual_conversion(driver):
    driver.get(BASE_URL + "/")
    manual = driver.find_element(By.ID, "manualInput")
    manual.send_keys(SAMPLE_METAR)
    convert_btn = driver.find_element(By.ID, "convertBtn")
    convert_btn.click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".result-item"))
    )
    items = driver.find_elements(By.CSS_SELECTOR, ".result-item")
    assert len(items) == 1
    assert "METAR" in items[0].text


def test_ui_multiple_files_conversion(driver):
    driver.get(BASE_URL + "/")
    with tempfile.TemporaryDirectory() as td:
        f1 = Path(td) / "m1.tac"
        f2 = Path(td) / "m2.tac"
        f1.write_text(SAMPLE_METAR)
        f2.write_text(SAMPLE_METAR_2)
        driver.execute_script(
            "document.getElementById('fileInput').removeAttribute('hidden');")
        file_input = driver.find_element(By.ID, "fileInput")
        file_input.send_keys(str(f1) + "\n" + str(f2))
        convert_btn = driver.find_element(By.ID, "convertBtn")
        convert_btn.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".result-item"))
        )
        items = driver.find_elements(By.CSS_SELECTOR, ".result-item")
        assert len(items) >= 2


def test_ui_zip_batch(driver):
    driver.get(BASE_URL + "/")
    manual = driver.find_element(By.ID, "manualInput")
    manual.send_keys(SAMPLE_METAR)
    zip_btn = driver.find_element(By.ID, "zipBtn")
    zip_btn.click()
    WebDriverWait(driver, 10).until(
        lambda d: "hidden" in d.find_element(
            By.ID, "spinner").get_attribute("class")
    )
    errors = [e for e in driver.find_elements(
        By.CSS_SELECTOR, "div") if "Conversion failed" in e.text or "ZIP conversion failed" in e.text]
    assert not errors
