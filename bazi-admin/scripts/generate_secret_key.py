"""
生成安全的 JWT SECRET_KEY
"""
import secrets

def generate_secret_key():
    """生成 32 字节的随机密钥（64 个十六进制字符）"""
    return secrets.token_hex(32)

if __name__ == "__main__":
    key = generate_secret_key()
    print("\n" + "="*70)
    print("🔐 JWT SECRET_KEY 生成成功")
    print("="*70)
    print(f"\n{key}\n")
    print("="*70)
    print("\n📝 请将上述密钥复制到 .env 文件中:")
    print(f"   SECRET_KEY={key}")
    print("\n⚠️  注意:")
    print("   1. 请妥善保管此密钥，不要泄露或提交到 Git")
    print("   2. 生产环境必须使用不同的密钥")
    print("   3. 密钥泄露后请立即更换")
    print("="*70 + "\n")
