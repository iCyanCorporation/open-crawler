# fetch_domains.py
def save_dummy_urls():
    # ダミーデータのURLリスト
    urls = [
        "http://example1.com",
        "http://example2.net",
        "http://example3.org"
    ]
    
    # テキストファイルにURLを1行ずつ書き込む
    with open("domain_list.txt", "w") as f:
        for url in urls:
            f.write(url + ",")
    print("created")

if __name__ == "__main__":
    try:
        save_dummy_urls()
    
    except Exception as e:
        print(e)

    finally:
        print("done")
