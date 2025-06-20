# 3D Gaussian Splatting 物体重建与新视图合成  


> 使用 **3D Gaussian Splatting（3D-GS）** 对真实物体进行重建，生成 360° 环绕视频，并计算 PSNR / SSIM / LPIPS
> 同时与 **TensoRF**（任务 1 加速 NeRF）和原版 NeRF 做效率与质量对比。  

---

## 1 运行环境

| 组件 | 版本 / 说明 |
|------|-------------|
| OS   | Ubuntu 22.04 (WSL2) |
| Python | 3.11（conda）|
| CUDA | cu128 |
| PyTorch | 2.7 |
| COLMAP | 3.9（本地编译）|
| FFmpeg | 4.4 |


<details>
<summary>一行命令安装</summary>

```bash
conda env create -n gsplat -f extern/gaussian-splatting/environment.yml
conda activate gsplat
```

## 2 项目目录
```
GAUSSIAN/
├── colmap/                     # COLMAP 脚本
├── data/my_object/             # 拍摄的 43 张照片 + COLMAP 输出
│   ├── input/                  # 原始 4284×5712 JPG
│   ├── distorted/              # COLMAP sparse + DB
│   ├── images{,_2,_4,_8}/      # convert.py 生成的多分辨率
│   └── sparse/ stereo/ …
├── extern/gaussian-splatting/  # 官方仓库（子模块）
├── outputs/                    # 训练/渲染结果
│   └── my_object_3dgs_r2/
│       ├── point_cloud/        # .ply 检查点
│       ├── renders/ours_30000/ # 43 张 PNG 渲染
│       ├── train/…             # TensorBoard 日志
│       └── chkpnt{5,15,30}000.pth
└── scripts/
    ├── train_gsplat.sh         # 一键训练脚本
    └── view_ply_matplotlib.py  # 点云快速预览
```

## 3 数据处理流程
> 拍摄 转台环拍 ≈ 43 张高分辨率照片
```
# 特征提取
colmap feature_extractor \
    --database_path database.db \
    --image_path    input \
    --ImageReader.single_camera 1 \
    --SiftExtraction.use_gpu 1 \
    --SiftExtraction.estimate_affine_shape true \
    --SiftExtraction.domain_size_pooling    true

# 全量匹配
colmap exhaustive_matcher \
    --database_path database.db \
    --SiftMatching.guided_matching 1

# 建图
colmap mapper \
    --database_path database.db \
    --image_path    input \
    --output_path   sparse

```
> 去畸变 + 生成多尺度图像
```
python convert.py \
  -s ../../data/my_object \
  --skip_matching \
  --resize \
  --no_gpu
```

## 4 训练命令
```
bash scripts/train_gsplat.sh          # 内容如下

# ~ 15k
python train.py \
  -s ../../data/my_object \
  -m ../../outputs/my_object_3dgs \
  --iterations 30000 \
  --test_iterations 5000 15000 30000 \
  --save_iterations 5000 15000 30000 \
  -r 2 \
  --eval

# 15k ~ 30k (由于显存问题)
python train.py \
  -s ../../data/my_object \
  -m ../../outputs/my_object_3dgs_r2 \
  --start_checkpoint ../../outputs/my_object_3dgs_r2/chkpnt15000.pth \
  --iterations 30000 \
  -r 2 \
  --data_device cpu \
  --densify_until_iter 10000 \
  --densify_grad_threshold 0.001 \
  --test_iterations 30000 \
  --save_iterations 30000 \
  --checkpoint_iterations 30000 \
  --disable_viewer
```
关键超参说明

| 参数| 值 |说明 |
|------|--------|----|
|iterations |30000 | 实际收敛轮次 |
|densify_until_iter|10000|	1w 以后不再增点，减小显存|
|densify_grad_threshold|1e-3|	调高阈值 → 剩余点更少|
|data_device|	cpu|高斯属性放 CPU，可把显存控制在 ~3.5 GB

## 5 渲染与视频
```
# 渲染
python render.py \
  --source_path ../../data/my_object \
  --model_path  ../../outputs/my_object_3dgs_r2 \
  --resolution 2 \
  --iteration 30000

# 合成视频
ffmpeg -y -framerate 30 -i ../../outputs/my_object_3dgs_r2/train/ours_30000/renders/%05d.png -c:v libx264 -pix_fmt yuv420p ../../outputs/my_object_3dgs_r2/train_video_r2.mp4
```

## 6 评估指标
```
python extern/gaussian-splatting/metrics.py \
       --model_paths outputs/my_object_3dgs_r2

```