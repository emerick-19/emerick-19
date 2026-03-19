import base64
import random
import string

# -----------------------------
# Utils
# -----------------------------
def random_var(length=6):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))


# -----------------------------
# Niveau 1 : Base64 encoding
# -----------------------------
def obfuscate_level1(ps_code):
    encoded = base64.b64encode(ps_code.encode('utf-16le')).decode()
    return encoded


# -----------------------------
# Niveau 2 : String splitting + IEX
# -----------------------------
def obfuscate_level2(ps_code):
    parts = []
    chunk_size = random.randint(3, 6)

    for i in range(0, len(ps_code), chunk_size):
        part = ps_code[i:i+chunk_size]
        parts.append(f'"{part}"')

    joined = "+".join(parts)
    obfuscated = f"IEX({joined})"
    return obfuscated


# -----------------------------
# Génération BAT
# -----------------------------
def generate_bat(encoded_command=None, inline_command=None):
    var_map = {c: random_var() for c in "abcde"}

    if encoded_command:
        bat = f"""@echo off
set {var_map['a']}=powershell
set {var_map['b']}=-NoProfile
set {var_map['c']}=-ExecutionPolicy Bypass
set {var_map['d']}=-EncodedCommand
set {var_map['e']}={encoded_command}

%{var_map['a']}% %{var_map['b']}% %{var_map['c']}% %{var_map['d']}% %{var_map['e']}%
"""
    else:
        bat = f"""@echo off
powershell -NoProfile -ExecutionPolicy Bypass -Command "{inline_command}"
"""

    return bat


# -----------------------------
# MAIN
# -----------------------------
def main():
    print("=== PowerShell Obfuscator Tool (Lab Only) ===")

    file = input("Enter path to .ps1 file: ")

    with open(file, "r", encoding="utf-8") as f:
        ps_code = f.read()

    print("\nChoose obfuscation level:")
    print("1 - Base64 (simple)")
    print("2 - String split + IEX")
    choice = input("Choice: ")

    if choice == "1":
        encoded = obfuscate_level1(ps_code)
        bat = generate_bat(encoded_command=encoded)

    elif choice == "2":
        obf = obfuscate_level2(ps_code)
        bat = generate_bat(inline_command=obf)

    else:
        print("Invalid choice")
        return

    output = input("Output .bat file name: ")

    with open(output, "w") as f:
        f.write(bat)

    print(f"\n[+] BAT file generated: {output}")


if __name__ == "__main__":
    main()
