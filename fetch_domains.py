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
            f.write(url + "\n")
    print("Dummy URLs saved to domain_list.txt")

if __name__ == "__main__":
    save_dummy_urls()
