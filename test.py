s = "北川青片乡西纳村至正河村公路工程北川县青片乡"
import cpca
df = cpca.transform([s])
print(df)

# import cv2
# import numpy as np
# img_path = 'E:\code\parse_contract\imgs\金牛区曹家巷驷马桥社区卫生服务中心装修改造设备提升工程\2 汇旺-凯月欣 驷马桥项目-空调采购合同 1486224\9.jpg'
# img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), -1)
# # 灰度化
# image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# # 二值化
# _, image = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)
# cv2.imwrite(img_path, image)



import sqlite3

def update_data(conn, new_data):
    cursor = conn.cursor()

    # 查询数据库中是否存在相同 ID 的数据
    cursor.execute("SELECT * FROM your_table WHERE id=?", (new_data['id'],))
    existing_data = cursor.fetchone()

    if existing_data:
        # 如果存在相同 ID 的数据，比较时间戳
        if (new_data['timestamp'] is not None and
                (existing_data['timestamp'] is None or new_data['timestamp'] > existing_data['timestamp'])):
            # 如果新数据时间戳较新，检查字段是否为空
            for key, value in new_data.items():
                if value is not None:
                    existing_data[key] = value
            # 更新数据库中的数据
            cursor.execute("UPDATE your_table SET timestamp=?, field1=?, field2=?, ... WHERE id=?",
                           (existing_data['timestamp'], existing_data['field1'], existing_data['field2'], ..., existing_data['id']))
            conn.commit()
            print("Data updated successfully.")
        else:
            print("Existing data is newer or has a valid timestamp. No update needed.")
    else:
        # 如果不存在相同 ID 的数据，插入新数据
        cursor.execute("INSERT INTO your_table (id, timestamp, field1, field2, ...) VALUES (?, ?, ?, ?, ...)",
                       (new_data['id'], new_data['timestamp'], new_data['field1'], new_data['field2'], ...))
        conn.commit()
        print("New data inserted successfully.")

# 示例新数据，注意 timestamp 可能为 None
new_data = {
    'id': 1,
    'timestamp': None,
    'field1': 'new_value1',
    'field2': None,  # Assume this is the field that can be None
    # Add other fields as needed
}

# 连接到数据库
conn = sqlite3.connect('your_database.db')

# 调用更新函数
update_data(conn, new_data)

# 关闭数据库连接
conn.close()
