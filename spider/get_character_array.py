def get_character_array() -> list:
    """从三元组文件提取去重人物列表"""
    characters = set()
    with open("../triples_processed.txt", "r", encoding="utf-8") as f:
        for line in f:
            subj, obj, _, _, _ = line.strip().split(",")
            characters.add(subj)
            characters.add(obj)
    return list(characters)

if __name__ == "__main__":
    chars = get_character_array()
    print(f"提取人物 {len(chars)} 个：{chars[:10]}...")
