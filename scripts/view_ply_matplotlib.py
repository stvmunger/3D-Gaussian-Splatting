import numpy as np
import matplotlib.pyplot as plt
from plyfile import PlyData
from mpl_toolkits.mplot3d import Axes3D

# 直接解析PLY文件（不依赖Open3D）
ply_path = "/home/kevin/projects/Gaussian/data/my_object/sparse/0/points3D.ply"
ply_data = PlyData.read(ply_path)
vertices = ply_data['vertex']

# 提取坐标和颜色
x = vertices['x']
y = vertices['y']
z = vertices['z']
r = vertices['red'] / 255.0
g = vertices['green'] / 255.0
b = vertices['blue'] / 255.0

# 创建3D散点图
fig = plt.figure(figsize=(12, 10))
ax = fig.add_subplot(111, projection='3d')

# 分批绘制避免内存溢出
batch_size = 5000
for i in range(0, len(x), batch_size):
    end_idx = min(i + batch_size, len(x))
    ax.scatter(
        x[i:end_idx], y[i:end_idx], z[i:end_idx],
        c=np.array([r[i:end_idx], g[i:end_idx], b[i:end_idx]]).T,
        s=0.1,  # 点大小
        depthshade=False  # 关闭深度阴影提升性能
    )

# 设置视角
ax.view_init(elev=30, azim=45)  # 仰角30度，方位角45度
ax.set_box_aspect([np.ptp(x), np.ptp(y), np.ptp(z)])  # 等比例缩放坐标轴

# 保存和显示
plt.savefig('point_cloud_view.png', dpi=300, bbox_inches='tight')
plt.title(f"Point Cloud: {len(x)} points")
plt.show()