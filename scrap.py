import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import environs


def auth(driver, email=None, password=None):
    driver.find_element(
        By.XPATH,
        '//*[@id="onetrust-accept-btn-handler"]',
    ).click()
    driver.find_element(
        By.XPATH,
        "/html/body/app-root/app-headerless-layout/div/div/div/app-login/div[2]/div[3]",
    ).click()
    driver.find_element(
        By.XPATH,
        "/html/body/app-root/app-headerless-layout/div/div/div/app-login/div[2]/div[3]/form/div[1]/div[1]/input",
    ).send_keys(email)
    driver.find_element(
        By.XPATH,
        "/html/body/app-root/app-headerless-layout/div/div/div/app-login/div[2]/div[3]/form/div[2]/div/input",
    ).send_keys(password)
    driver.find_element(
        By.XPATH,
        "/html/body/app-root/app-headerless-layout/div/div/div/app-login/div[2]/div[3]/form/button",
    ).click()


def go_to_calendar(driver):
    driver.find_element(
        By.XPATH, "/html/body/app-root/app-header-laout/div/div/app-menu/div/div/a[6]"
    ).click()
    time.sleep(1)


def create_df(data=None):
    return pd.DataFrame(
        data=data,
        columns=[
            "points",
            "item",
            "team",
            "role",
            "opponent",
        ],
    )


def fill_df(driver, df):
    roles = ["top", "jungle", "mid", "bot", "support", "coach"]
    team_1 = driver.find_element(
        By.XPATH,
        "/html/body/app-root/app-header-laout/div/div/div/app-match/div[1]/div/div[2]/img",
    ).get_attribute("alt")
    team_2 = driver.find_element(
        By.XPATH,
        "/html/body/app-root/app-header-laout/div/div/div/app-match/div[1]/div/div[4]/img",
    ).get_attribute("alt")

    items = driver.find_elements(By.XPATH, "//*[@class='item-name']")
    items = items[0 : len(items) // 2]
    nitems = len(items)
    stats = driver.find_elements(
        By.XPATH,
        "//*[not(contains(@class, 'mh-stat-desktop')) and contains(@class, 'mh-stat') and not(contains(@class, 'mh-stat-list'))]",
    )
    stats = stats[0 : nitems * len(roles) * 2]
    lst = []
    for i, stat in enumerate(stats):
        if stat.text == "-":
            continue
        lst.append(
            [
                stat.text,
                items[i % nitems].text,
                team_1 if i < nitems * 6 else team_2,
                roles[(i // nitems) % 6],
                team_2 if i < nitems * 6 else team_1,
            ]
        )
    return pd.concat([df, create_df(lst)], ignore_index=True)


def main():
    env = environs.Env()
    env.read_env()
    df = create_df()
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    options.page_load_strategy = "none"
    chrome_path = ChromeDriverManager().install()
    chrome_service = Service(chrome_path)
    driver = Chrome(options=options, service=chrome_service)
    driver.implicitly_wait(5)

    driver.get(f"{env('FANTASY_LEAGUE_URL')}/login")
    time.sleep(2)
    auth(driver, env("FANTASY_EMAIL"), env("FANTASY_PWD"))
    go_to_calendar(driver)

    ngames = len(driver.find_elements(By.XPATH, "//*[@class='match played']"))

    for i in range(0, ngames):
        games = driver.find_elements(By.XPATH, f"//*[@class='match played']")
        games[i].click()
        time.sleep(2)
        df = fill_df(driver, df)
        print(df)
        driver.back()
        time.sleep(1)

    df.to_csv("data/items-stats.csv", index=False)

    exit()


if __name__ == "__main__":
    main()
