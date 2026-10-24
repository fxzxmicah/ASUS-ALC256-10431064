## 公开文档

- 项目与包内 README 面向公开读者；验证状态必须区分已经实测的初始化序列与后续代码整理，不扩大硬件验证范围。

- 所有准备发布到远程仓库的文档面向公开读者，不能写成只对当前对话中的用户有意义的答复。
- 先交代项目解决的问题、适用范围和当前状态；不假定读者知道对话历史、个人密钥名称或本地目录布局。
- 文档保持项目说明的风格，避免事无巨细的个人操作指导及对已放弃方案的解释。

## Patch 生成规则

- 所有 patch 只能由 Git 生成，例如 `git diff`、`git format-patch`。
- 先在对应源码的 Git 工作区修改源码，再由 Git 导出 patch。
- 不得手写或直接修改 patch 的 diff 内容、hunk、行号、上下文和统计信息，不得使用 difflib 等非 Git 方式生成。

## 长期维护约束

- 构建产物只发布到 GitHub Releases；不加入 RPM GPG 签名或 OSS 上传流程。
- 日常新内核构建应只需触发 workflow；不得将目标内核版本写死在 spec 或安装工具中。
- 保留 workflow、SOURCES、SPECS 的职责结构。参考项目为 `fxzxmicah/nvidia-driver`，有本地副本时优先读取；对参考仓库的修改须在用户授权范围内。
- 直接维护 `SOURCES/realtek` 中的 Fedora 下游源码及必要私有头文件，通过目标 kernel-devel 的 Kbuild 构建。不能用 vanilla Linux 源码替代 Fedora 下游基线。
- 维护时同步更新 Fedora 源码基线、`FEDORA` 来源记录、`fedora-source.sha256` 和说明用 patch。先审阅 Fedora 更新并适配实验逻辑，不能用机械导出差异代替源码同步或适配。说明 patch 和基线校验表仅留在仓库，不列入 spec Source，不包含在二进制 RPM 或 SRPM 中。
- RPM Name 固定，仅使用 `kernel_ver` 表示 version、`kernel_rel` 表示 release，需要完整版本时拼接为 `%{kernel_ver}-%{kernel_rel}`；内核模块路径使用 `%{kernel_ver}-%{kernel_rel}.%{_arch}`。采用 `installonlypkg(kernel-module)` 实现多版本共存。分支名决定 Fedora container 版本。
- depmod 配置文件按目标内核版本命名；override 直接在 `%install` 写入并限定该内核。许可证直接在 `%install` 安装。
- 构建过程不下载 kernel SRPM、不应用 patch，不另建 ABI 测试框架。spectool 按整个 spec 获取来源，不在 workflow 中限定 Source 编号。
- 不提供专用 dracut 配置，模块是否进入 initramfs 交由系统默认规则处理；已有镜像含被替换模块时，安装签名完成后及卸载后需更新目标 initramfs。
- 安装脚本只做本地签名和 depmod；卸载 RPM 恢复根文件系统中的原模块选择。不另造激活、回滚或签名配置框架，密钥路径和签名逻辑沿用参考仓库；缺少密钥或证书时跳过签名，不增加安装失败条件。
- 内核及模块编译、RPM 构建检查通过远程 CI 完成；脚本语法检查不等于模块编译验证。
- 私钥只留用户电脑；由本地 RPM 脚本触发签名。不能覆盖 Fedora 原模块、关闭 Secure Boot，或在失败时交付旧模块。
- 未经实机验证不得宣称修复有效；上游正式补丁必须基于真实验证结果。
