# 🎯 双色球AI智能预测系统 v1.1

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/LJQ-HUB-cmyk/SSQ-LightGBM-Log-SVC-V1.1.svg)](https://github.com/LJQ-HUB-cmyk/SSQ-LightGBM-Log-SVC-V1.1/stargazers)

一个基于机器学习和数据挖掘技术的双色球彩票智能分析预测系统，集成了LightGBM、关联规则挖掘、Optuna参数优化等先进算法。

## 🌟 **核心特性**

### 🤖 **智能算法引擎**
- **LightGBM机器学习**：为每个球号训练独立的二分类预测模型
- **关联规则挖掘**：使用Apriori算法发现号码间的关联模式
- **Optuna自动优化**：智能搜索最优参数组合（100次试验）
- **多因子评分系统**：综合频率、遗漏、ML预测等多维度评分

### 📊 **数据分析引擎**
- **滑动窗口分析**：支持自定义窗口大小，平衡时效性与稳定性
- **频率与遗漏统计**：精确计算当前遗漏、平均间隔、最大遗漏
- **模式识别**：分析和值、跨度、奇偶比、三区分布等模式
- **特征工程**：创建滞后特征、交互特征，提升预测准确性

### 🎯 **策略生成系统**
- **单式推荐**：生成15注高质量单式投注组合
- **复式参考**：提供Top7红球+Top7蓝球复式投注建议
- **反向思维策略**：移除得分最高组合，规避"过热"号码
- **多样性控制**：确保推荐组合间的差异性，降低风险

### 📈 **回测验证系统**
- **历史回测**：基于最近100期数据验证策略有效性
- **ROI计算**：精确计算投资回报率和盈亏分析
- **中奖统计**：详细统计各奖级命中情况
- **性能监控**：实时监控预测准确率和策略表现

### 📱 **智能推送系统**
- **微信实时推送**：基于WxPusher的分析报告和验证结果推送
- **分批推送**：智能分割长内容，确保推送完整性
- **多场景推送**：支持分析报告、验证结果、错误通知等多种场景

## 📦 **系统架构**

```
📁 SSQ-LightGBM-Log-SVC-V1.1/
├── 🧠 ssq_analyzer.py           # 核心分析引擎（1246行）
├── 🔍 ssq_bonus_calculation.py  # 验证计算模块（453行）
├── 📡 ssq_data_processor.py     # 数据获取处理（347行）
├── 📱 ssq_wxpusher.py          # 微信推送模块（520行）
├── 📋 requirements.txt         # 依赖配置
├── 📄 README.md               # 项目文档
├── 📊 latest_ssq_analysis.txt  # 最新分析报告
├── 💰 latest_ssq_calculation.txt # 最新验证结果
└── 📁 .github/                # GitHub工作流配置
```

## 🚀 **快速开始**

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/LJQ-HUB-cmyk/SSQ-LightGBM-Log-SVC-V1.1.git
cd SSQ-LightGBM-Log-SVC-V1.1

# 安装依赖
pip install -r requirements.txt

# 或使用conda
conda install pandas numpy requests beautifulsoup4 optuna lightgbm mlxtend lxml
```

### 2. 数据获取
```bash
# 获取最新双色球历史数据
python ssq_data_processor.py
```

### 3. 运行分析
```bash
# 快速分析模式（使用默认参数）
python ssq_analyzer.py

# 或修改 ENABLE_OPTUNA_OPTIMIZATION = True 启用优化模式
# 注意：优化模式耗时较长（约1-2小时），但效果更佳
```

### 4. 验证结果
```bash
# 验证最新一期的预测结果
python ssq_bonus_calculation.py
```

## ⚙️ **核心算法详解**

### 🎯 **多因子评分算法**
```python
# 红球综合评分公式
score = (
    频率分数 * 28.19 +           # 历史出现频率
    遗漏分数 * 19.92 +           # 当前遗漏状态  
    最大遗漏比率分数 * 16.12 +    # 博冷策略
    近期频率分数 * 15.71 +       # 追热策略
    ML预测分数 * 22.43          # 机器学习预测
)
```

### 🔗 **关联规则挖掘**
```python
# ARM算法参数（可通过Optuna优化）
min_support = 0.01      # 最小支持度
min_confidence = 0.53   # 最小置信度  
min_lift = 1.53        # 最小提升度

# 发现号码间的关联模式，如：{1,6} -> {22} (置信度85%, 提升度2.1)
```

### 🧠 **LightGBM预测模型**
```python
# 每个球号独立训练二分类模型
features = [
    '滞后特征(1,3,5,10期)',
    '交互特征(和值×奇数个数)',  
    '历史统计特征',
    '模式特征'
]

# 模型参数优化配置
lgbm_params = {
    'learning_rate': 0.04,
    'n_estimators': 100,
    'num_leaves': 15,
    'min_child_samples': 15,
    'feature_fraction': 0.7,
    'bagging_fraction': 0.8
}
```

## 📊 **系统表现**

### 🎯 **回测结果示例**
```
回测周期: 最近100期 | 每期15注 | 总投入: 3,000元
├── 五等奖: 18次 (180元)
├── 六等奖: 92次 (460元) 
├── 总回报: 640元
├── ROI: -78.67%
└── 蓝球覆盖率: 17%的期数至少命中1注蓝球
```

### 📈 **优化效果**
- **参数优化前**: 使用默认参数，回测表现一般
- **参数优化后**: Optuna自动寻找最优参数组合，显著提升策略表现
- **滑动窗口优化**: 频率窗口60期、模式窗口70期，更好平衡时效性

## 📱 **微信推送配置**

### 1. 获取WxPusher配置
1. 访问 [WxPusher官网](https://wxpusher.zjiecode.com)
2. 创建应用获取 `APP_TOKEN`
3. 关注应用获取 `USER_UID`

### 2. 配置推送参数
```python
# 在 ssq_wxpusher.py 中配置
APP_TOKEN = "AT_xxxxxxxxxx"
USER_UIDS = ["UID_xxxxxxxxxx"]
TOPIC_IDS = [12345]
```

### 3. 推送内容
- 📊 **分析报告**: 包含15注推荐、复式参考、优化结果
- ✅ **验证报告**: 包含中奖情况、投资回报分析
- ⚠️ **错误通知**: 系统运行异常时的及时提醒

## 🔧 **高级配置**

### 1. 优化模式开关
```python
# 在 ssq_analyzer.py 中修改
ENABLE_OPTUNA_OPTIMIZATION = True   # 启用参数优化
OPTIMIZATION_TRIALS = 100          # 优化试验次数
```

### 2. 滑动窗口配置
```python
DEFAULT_WINDOW_PARAMS = {
    'FREQUENCY_WINDOW': 50,    # 频率统计窗口
    'PATTERN_WINDOW': 50,      # 模式分析窗口
    'ASSOCIATION_WINDOW': 50,  # 关联规则窗口
    'ML_TRAINING_WINDOW': 200, # 机器学习训练窗口
}
```

### 3. 反向思维策略
```python
ENABLE_FINAL_COMBO_REVERSE = True   # 启用反向思维
ENABLE_REVERSE_REFILL = True        # 移除后补充组合
```

## 📋 **使用建议**

### 💡 **投注策略建议**
1. **单式投注**: 选择评分最高的3-5注进行投注
2. **复式投注**: 根据Top7红球和蓝球构建复式投注
3. **分散投注**: 避免集中投注，分散到多期降低风险
4. **理性投注**: 系统仅供参考，请理性投注，量力而行

### ⚠️ **风险提示**
- 本系统基于历史数据分析，无法保证未来结果
- 彩票具有随机性，任何预测都存在不确定性
- 请严格控制投注金额，避免过度投注
- 建议将此系统作为娱乐和学习工具使用

### 🔄 **最佳实践**
1. **定期更新数据**: 使用 `ssq_data_processor.py` 获取最新数据
2. **定期运行优化**: 每月运行一次Optuna优化更新参数
3. **关注验证结果**: 通过 `ssq_bonus_calculation.py` 跟踪策略表现
4. **调整策略参数**: 根据回测结果适当调整投注策略

## 🤝 **贡献指南**

我们欢迎社区贡献！请遵循以下步骤：

1. Fork本项目
2. 创建特性分支: `git checkout -b feature/amazing-feature`
3. 提交更改: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 创建Pull Request

## 📄 **更新日志**

### v1.1 (2025-06-26)
- ✨ 新增Optuna参数自动优化功能
- 🚀 实现滑动窗口参数优化
- 📱 集成微信推送功能
- 🔧 优化关联规则挖掘算法
- 📊 改进回测验证系统

### v1.0 (2025-06-20)
- 🎯 初始版本发布
- 🤖 实现LightGBM预测模型
- 📈 实现多因子评分算法
- 🔍 实现历史数据回测验证

## 📞 **技术支持**

- 📧 **邮箱**: [your-email@example.com]
- 🐛 **Bug报告**: [Issues](https://github.com/LJQ-HUB-cmyk/SSQ-LightGBM-Log-SVC-V1.1/issues)
- 💡 **功能请求**: [Discussions](https://github.com/LJQ-HUB-cmyk/SSQ-LightGBM-Log-SVC-V1.1/discussions)

## 📜 **开源协议**

本项目采用 [MIT License](LICENSE) 开源协议。

---

⭐ **如果这个项目对您有帮助，请给我们一个Star！** ⭐

💰 **声明**: 本项目仅供学习和研究使用，请理性投注，量力而行！


项目运行后的日常更新：

# 1. 查看文件状态
git status

# 2. 添加修改的文件
git add .

# 3. 提交更改
git commit -m "📊 新增最近5期内开出过的号码 + 6期内没有开出过号码"

# 4. 推送到远程仓库
git push origin main
🔧 常见Git命令
# 查看提交历史
git log --oneline

# 查看远程仓库信息
git remote -v

# 拉取最新更改
git pull origin main

# 查看分支
git branch -a

# 创建新分支
git checkout -b feature/new-algorithm