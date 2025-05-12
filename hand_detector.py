import os
import cv2
import math
import pandas as pd
import mediapipe as mp

# 初始化 Mediapipe 手部模型
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# 各类动作对应的关键点索引对
angle_definitions = {
    "index": (6, 5),
    "middle": (10, 9),
    "pinky": (18, 17),
    "ring": (14, 13),
    "thumb": (3, 1),
    "wrist_extension": (5, 0),
    "wrist_flexion": (5, 0)
}


# 计算关键点连线与水平线之间的夹角（以水平线为参考）
def calculate_angle(p1, p2):
    """
    计算从点2指向点1的向量 与 点2指向左水平线（-X方向）的夹角（带符号）
    正：点1在点2上方；负：点1在点2下方
    """
    vx = p1.x - p2.x
    vy = p1.y - p2.y

    base_vx, base_vy = -1, 0

    dot = vx * base_vx + vy * base_vy
    det = vx * base_vy - vy * base_vx

    angle_rad = math.atan2(det, dot)
    angle_deg = math.degrees(angle_rad)

    return round(-angle_deg, 1)  # ← 精度保留到 0.1 度


# 主处理函数
def process_hand_angles(root_folder):
    categories = list(angle_definitions.keys())
    result = {category: [] for category in categories}

    for category in categories:
        point_idx1, point_idx2 = angle_definitions[category]
        folder_path = os.path.join(root_folder, category)

        for i in range(1, 28):  # 图片编号从1到27
            image_path = os.path.join(folder_path, f"{i}.png")
            image = cv2.imread(image_path)

            if image is None:
                print(f"警告：无法读取图片 {image_path}")
                result[category].append(0)
                continue

            # 将 BGR 图像转换为 RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            output = hands.process(image_rgb)

            if output.multi_hand_landmarks:
                # 获取手部关键点
                landmarks = output.multi_hand_landmarks[0].landmark
                p1 = landmarks[point_idx1]
                p2 = landmarks[point_idx2]
                angle = calculate_angle(p1, p2)
                result[category].append(angle)
            else:
                # 无法检测到手部
                result[category].append(0)

    return result


# 保存结果为 Excel 文件
def save_to_excel(data_dict, output_path="person6.xlsx"):
    df = pd.DataFrame(data_dict, index=[str(i) for i in range(1, 28)])
    df.index.name = "Image Index"
    df.to_excel(output_path)
    print(f"✅ 成功保存结果至 {output_path}")


# ===== 主执行入口 =====
if __name__ == "__main__":
    # 指定包含 index/middle/pinky/... 子文件夹的主目录
    ROOT_FOLDER = "datas/single/6"  # <<< 修改为你自己的路径

    angles = process_hand_angles(ROOT_FOLDER)
    save_to_excel(angles)
