import json

def main():
    with open("./output/pages/page_content.txt", "w") as f_o:
        with open("./output/pages/out_pages.jsonl") as f:
            for line in f:
                doc = json.loads(line)
                
                f_o.write(doc["url"] + "\n\n")
                f_o.write(doc["content_text"] + "\n\n")
                f_o.write("parent:" + (doc["parent_url"] or "") + "\n\n")
                f_o.write("-"*100 + "\n\n")


main()

