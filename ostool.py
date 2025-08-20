import os
import errno
import shutil
from pathlib import Path


def force_symlink(src_path: Path, dst_path: Path, target_is_directory: bool = False):
    """
    创建符号链接：
    - 如果目标已存在且是符号链接:
        - 指向相同 -> 跳过
        - 指向不同 -> 删除后重建
    - 如果目标已存在且为真实目录/文件 -> 抛异常（不删除，保护数据）
    - 否则直接创建
    """
    if dst_path.exists() or dst_path.is_symlink():
        if dst_path.is_symlink():
            current_target = dst_path.readlink()
            if current_target.resolve() == src_path.resolve():
                # print(f"Skipped (already correct link): {dst_path} -> {current_target}")
                return
            else:
                dst_path.unlink()  # 删除旧符号链接

    dst_path.symlink_to(src_path, target_is_directory=target_is_directory)
    # print(f"Symlink created: {dst_path} -> {src_path}")


def copy_with_symlink(src: str, dst: str):
    """
    在 dst 位置创建 src 文件夹的符号链接副本。
    如果 dst 已存在，会报错。
    """
    src_path = Path(src).resolve()
    dst_path = Path(dst)

    if not src_path.exists():
        raise FileNotFoundError(f"源路径不存在: {src}")

    dst_path.parent.mkdir(parents=True, exist_ok=True)

    # Windows 下创建符号链接目录需要管理员权限，或启用"系统-开发者选项-开发人员模式"
    force_symlink(src_path, dst_path, target_is_directory=True)


def move_folder(src: str, dst: str) -> None:
    """
    移动或硬链接复制文件夹
    :param src: 源路径
    :param dst: 目标路径
    """
    if not os.path.exists(src):
        raise FileNotFoundError(f"源路径不存在: {src}")

    os.makedirs(os.path.dirname(dst), exist_ok=True)

    if os.path.exists(dst):
        err = FileExistsError(errno.EEXIST, "目标路径已存在")
        err.filename = src
        err.filename2 = dst
        raise err

    shutil.move(src, dst)


def normalize_path(path: str) -> str:
    # 统一分隔符
    path = path.replace("\\", "/")
    # 切分 -> 去掉空白 -> 去掉空字符串
    parts = [p.strip() for p in path.split("/") if p.strip()]
    # 拼接
    return "/".join(parts)
