"""
Generates high-quality synthetic road defect texture assets for RHI demo.
"""
import os
import random
from PIL import Image, ImageDraw, ImageFilter

os.makedirs("frontend/assets", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

def generate_asphalt_base(width=800, height=600, base_color=(45, 48, 52)):
    img = Image.new("RGB", (width, height), base_color)
    pixels = img.load()
    for y in range(height):
        for x in range(width):
            noise = random.randint(-18, 18)
            r = max(0, min(255, base_color[0] + noise))
            g = max(0, min(255, base_color[1] + noise))
            b = max(0, min(255, base_color[2] + noise))
            pixels[x, y] = (r, g, b)
    # Add road lane markings (white or yellow dashed)
    draw = ImageDraw.Draw(img)
    # Top perspective road edges
    draw.line([(0, height - 30), (width, height - 30)], fill=(30, 32, 35), width=3)
    # Center dashed lane
    for y in range(0, height, 80):
        draw.line([(width // 2, y), (width // 2, y + 45)], fill=(220, 220, 220), width=6)
    return img

def create_pothole_image(filename, severity="HIGH"):
    img = generate_asphalt_base(800, 600, (42, 45, 48))
    draw = ImageDraw.Draw(img)
    
    cx, cy = 400, 340
    rx, ry = 130, 85

    # Outer distressed asphalt ring
    for r_offset in range(30, 0, -5):
        draw.ellipse(
            [cx - rx - r_offset, cy - ry - r_offset // 2, cx + rx + r_offset, cy + ry + r_offset // 2],
            fill=None,
            outline=(25, 28, 30),
            width=3
        )

    # Deep pothole pit
    draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(15, 16, 18))
    
    # Internal depth shadow & rubble
    draw.ellipse([cx - rx + 20, cy - ry + 15, cx + rx - 20, cy + ry - 10], fill=(8, 8, 10))
    for _ in range(40):
        rx_stone = cx + random.randint(-rx + 15, rx - 15)
        ry_stone = cy + random.randint(-ry + 10, ry - 10)
        draw.rectangle([rx_stone, ry_stone, rx_stone + random.randint(3, 8), ry_stone + random.randint(3, 6)], fill=(65, 68, 72))

    # Radial fissure cracks
    for _ in range(12):
        angle_x = random.choice([-1, 1]) * random.randint(rx, rx + 120)
        angle_y = random.choice([-1, 1]) * random.randint(ry, ry + 80)
        draw.line([(cx, cy), (cx + angle_x, cy + angle_y)], fill=(20, 22, 24), width=random.randint(1, 3))

    img = img.filter(ImageFilter.SMOOTH_MORE)
    img.save(f"frontend/assets/{filename}", quality=95)
    img.save(f"uploads/{filename}", quality=95)
    print(f"Generated {filename}")

def create_crack_image(filename):
    img = generate_asphalt_base(800, 600, (48, 50, 55))
    draw = ImageDraw.Draw(img)

    # Draw extensive alligator / spiderweb crack network
    nodes = [(random.randint(150, 650), random.randint(150, 500)) for _ in range(35)]
    for n1 in nodes:
        for n2 in nodes:
            dist = ((n1[0] - n2[0])**2 + (n1[1] - n2[1])**2)**0.5
            if dist < 110 and random.random() > 0.4:
                draw.line([n1, n2], fill=(12, 14, 16), width=random.randint(2, 4))
                # Micro-fissures
                mid = ((n1[0] + n2[0]) // 2 + random.randint(-10, 10), (n1[1] + n2[1]) // 2 + random.randint(-10, 10))
                draw.line([n1, mid], fill=(18, 20, 22), width=2)
                draw.line([mid, n2], fill=(18, 20, 22), width=2)

    img.save(f"frontend/assets/{filename}", quality=95)
    img.save(f"uploads/{filename}", quality=95)
    print(f"Generated {filename}")

def create_repaired_image(filename):
    img = generate_asphalt_base(800, 600, (40, 42, 45))
    draw = ImageDraw.Draw(img)

    # Freshly sealed black asphalt patch rectangle with rounded edges
    cx, cy = 400, 340
    rx, ry = 160, 110
    draw.rounded_rectangle(
        [cx - rx, cy - ry, cx + rx, cy + ry],
        radius=25,
        fill=(22, 24, 26),
        outline=(15, 16, 18),
        width=4
    )
    # Add subtle asphalt roller texture marks
    for y_mark in range(cy - ry + 15, cy + ry - 15, 20):
        draw.line([(cx - rx + 15, y_mark), (cx + rx - 15, y_mark)], fill=(28, 30, 34), width=2)

    img.save(f"frontend/assets/{filename}", quality=95)
    img.save(f"uploads/{filename}", quality=95)
    print(f"Generated {filename}")

def create_failed_repair_image(filename):
    img = generate_asphalt_base(800, 600, (40, 42, 45))
    draw = ImageDraw.Draw(img)

    # Poor quality patch with reopening crack and depression
    cx, cy = 400, 340
    rx, ry = 150, 100
    draw.rounded_rectangle([cx - rx, cy - ry, cx + rx, cy + ry], radius=20, fill=(28, 30, 32), outline=(18, 20, 22), width=2)
    # Severe reopening fissure through the patch
    draw.line([(cx - 90, cy - 40), (cx, cy), (cx + 80, cy + 30)], fill=(8, 8, 8), width=5)
    draw.line([(cx - 30, cy + 20), (cx + 30, cy - 10)], fill=(8, 8, 8), width=3)
    draw.ellipse([cx - 40, cy - 25, cx + 40, cy + 25], fill=(12, 12, 14))

    img.save(f"frontend/assets/{filename}", quality=95)
    img.save(f"uploads/{filename}", quality=95)
    print(f"Generated {filename}")

create_pothole_image("sample_pothole_1.jpg", "HIGH")
create_pothole_image("sample_pothole_2.jpg", "CRITICAL")
create_crack_image("sample_crack_1.jpg")
create_repaired_image("sample_repaired_1.jpg")
create_failed_repair_image("sample_failed_repair.jpg")
print("All sample assets generated successfully!")
