# Node.js 安装指南

由于系统权限限制，需要手动安装 Node.js。以下是几种安装方式：

## 方式 1：使用 Homebrew（推荐，但需要修复权限）

### 步骤 1：修复 Homebrew 权限
```bash
sudo chown -R $(whoami) /usr/local/Cellar /usr/local/Frameworks /usr/local/Homebrew /usr/local/bin /usr/local/etc /usr/local/include /usr/local/lib /usr/local/opt /usr/local/sbin /usr/local/share /usr/local/var/homebrew
```

### 步骤 2：安装 Node.js
```bash
brew install node
```

## 方式 2：使用 nvm（Node Version Manager，推荐）

nvm 安装到用户目录，不需要系统权限：

```bash
# 安装 nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 重新加载 shell 配置
source ~/.zshrc

# 安装最新的 LTS 版本 Node.js
nvm install --lts

# 使用该版本
nvm use --lts
```

## 方式 3：从官网下载安装包

1. 访问 https://nodejs.org/
2. 下载 macOS 安装包（.pkg 文件）
3. 双击安装包，按照提示完成安装

## 验证安装

安装完成后，在终端运行：

```bash
node --version
npm --version
```

如果显示版本号，说明安装成功。

## 安装前端依赖

Node.js 安装成功后，运行：

```bash
cd /Users/luohongwenye/bijia/frontend
npm install
```
