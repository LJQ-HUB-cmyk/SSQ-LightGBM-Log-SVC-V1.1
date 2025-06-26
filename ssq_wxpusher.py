# -*- coding: utf-8 -*-
"""
双色球微信推送模块
================

提供微信推送功能，用于推送双色球分析报告和验证报告
"""

import requests
import logging
import json
import os
from datetime import datetime
from typing import Optional, List, Dict
from math import comb

# 微信推送配置
# 支持从环境变量读取配置（用于GitHub Actions等CI环境）
APP_TOKEN = os.getenv("WXPUSHER_APP_TOKEN", "AT_FInZJJ0mUU8xvQjKRP7v6omvuHN3Fdqw")
USER_UIDS = os.getenv("WXPUSHER_USER_UIDS", "UID_yYObqdMVScIa66DGR2n2PCRFL10w").split(",")
TOPIC_IDS = [int(x) for x in os.getenv("WXPUSHER_TOPIC_IDS", "39909").split(",") if x.strip()]

def get_latest_verification_result() -> Optional[Dict]:
    """获取最新的验证结果
    
    Returns:
        最新验证结果字典，如果没有则返回None
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        calc_file = os.path.join(script_dir, 'latest_ssq_calculation.txt')
        
        if not os.path.exists(calc_file):
            return None
            
        with open(calc_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析最新的验证记录
        lines = content.split('\n')
        
        # 查找最新的评估记录
        for i, line in enumerate(lines):
            if line.startswith('评估时间:'):
                # 解析评估信息
                result = {}
                
                # 解析期号
                for j in range(i, min(i+20, len(lines))):
                    if lines[j].startswith('评估期号'):
                        result['eval_period'] = lines[j].split(':')[1].strip().split()[0]
                    elif lines[j].startswith('开奖号码:'):
                        # 解析开奖号码: 红球 [2, 3, 15, 21, 22, 33] 蓝球 6
                        draw_line = lines[j]
                        if '红球' in draw_line and '蓝球' in draw_line:
                            try:
                                import re
                                red_match = re.search(r'红球\s*\[([^\]]+)\]', draw_line)
                                blue_match = re.search(r'蓝球\s*(\d+)', draw_line)
                                
                                if red_match and blue_match:
                                    red_nums = [int(x.strip()) for x in red_match.group(1).split(',')]
                                    blue_num = int(blue_match.group(1))
                                    result['prize_red'] = red_nums
                                    result['prize_blue'] = blue_num
                            except:
                                pass
                    elif lines[j].startswith('总奖金:'):
                        try:
                            amount_str = lines[j].split(':')[1].strip().replace('元', '').replace(',', '')
                            result['total_prize'] = int(amount_str) if amount_str.isdigit() else 0
                        except:
                            result['total_prize'] = 0
                
                return result if result else None
                
        return None
        
    except Exception as e:
        logging.error(f"获取最新验证结果失败: {e}")
        return None

def send_wxpusher_message(content: str, title: str = None, topicIds: List[int] = None, uids: List[str] = None) -> Dict:
    """发送微信推送消息
    
    Args:
        content: 消息内容
        title: 消息标题
        topicIds: 主题ID列表，默认使用全局配置
        uids: 用户ID列表，默认使用全局配置
    
    Returns:
        API响应结果字典
    """
    url = "https://wxpusher.zjiecode.com/api/send/message"
    headers = {"Content-Type": "application/json"}
    
    data = {
        "appToken": APP_TOKEN,
        "content": content,
        "uids": uids or USER_UIDS,
        "topicIds": topicIds or TOPIC_IDS,
        "summary": title or "双色球推荐更新",
        "contentType": 1,  # 1=文本，2=HTML
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if result.get("success", False):
            logging.info(f"微信推送成功: {title}")
            return {"success": True, "data": result}
        else:
            logging.error(f"微信推送失败: {result.get('msg', '未知错误')}")
            return {"success": False, "error": result.get('msg', '推送失败')}
            
    except requests.exceptions.RequestException as e:
        logging.error(f"微信推送网络错误: {e}")
        return {"success": False, "error": f"网络错误: {str(e)}"}
    except Exception as e:
        logging.error(f"微信推送异常: {e}")
        return {"success": False, "error": f"未知异常: {str(e)}"}

def send_analysis_report(report_content: str, period: int, recommendations: List[str], 
                         complex_red: List[str] = None, complex_blue: List[str] = None,
                         optuna_summary: Dict = None, backtest_stats: Dict = None) -> Dict:
    """发送双色球分析报告
    
    Args:
        report_content: 完整的分析报告内容
        period: 预测期号
        recommendations: 推荐号码列表
        complex_red: 复式红球列表
        complex_blue: 复式蓝球列表
        optuna_summary: Optuna优化摘要
        backtest_stats: 回测统计数据
    
    Returns:
        推送结果字典
    """
    title = f"🎯 双色球第{period}期预测报告"
    
    # 提取关键信息制作详细版推送
    try:
        # 获取最新验证结果
        latest_verification = get_latest_verification_result()
        
        # 构建单式推荐内容 - 显示所有推荐号码，采用紧凑格式
        rec_summary = ""
        if recommendations:
            for i, rec in enumerate(recommendations):
                # 提取号码部分，简化格式
                import re
                red_match = re.search(r'红球\s*\[([^\]]+)\]', rec)
                blue_match = re.search(r'蓝球\s*\[(\d+)\]', rec)
                
                if red_match and blue_match:
                    # 保持红球号码之间的空格，确保格式统一
                    red_nums_list = [x.strip() for x in red_match.group(1).split()]
                    red_nums = ' '.join(f'{int(x):02d}' for x in red_nums_list if x.isdigit())
                    blue_num = f'{int(blue_match.group(1)):02d}'
                    rec_summary += f"第{i+1:2d}注: {red_nums} + {blue_num}\n"
                else:
                    # 如果解析失败，使用原始格式但简化
                    rec_summary += f"第{i+1:2d}注: {rec}\n"
        
        # 构建复式参考内容
        complex_summary = ""
        if complex_red and complex_blue:
            # 计算复式组合数：C(红球数,6) * 蓝球数
            red_combinations = comb(len(complex_red), 6) if len(complex_red) >= 6 else 0
            total_combinations = red_combinations * len(complex_blue)
            
            complex_summary = f"""
📦 复式参考：
红球({len(complex_red)}个): {' '.join(complex_red)}
蓝球({len(complex_blue)}个): {' '.join(complex_blue)}

💡 复式共可组成 {total_combinations:,} 注
💰 投注成本: {total_combinations * 2:,} 元(单注2元)"""
        
        # 构建优化信息
        optuna_info = ""
        if optuna_summary and optuna_summary.get('status') == '完成':
            optuna_info = f"🔬 Optuna优化得分: {optuna_summary.get('best_value', 0):.2f}\n"
        
        # 构建回测信息
        backtest_info = ""
        if backtest_stats:
            prize_counts = backtest_stats.get('prize_counts', {})
            if prize_counts:
                prize_info = []
                for prize, count in prize_counts.items():
                    if count > 0:
                        prize_info.append(f"{prize}x{count}")
                if prize_info:
                    backtest_info = f"📊 最近回测: {', '.join(prize_info)}\n"
        
        # 构建最新验证结果摘要
        verification_summary = ""
        if latest_verification:
            verification_summary = f"""
📅 最新验证（第{latest_verification.get('eval_period', '未知')}期）：
🎱 开奖: 红球 {' '.join(f'{n:02d}' for n in latest_verification.get('prize_red', []))} 蓝球 {latest_verification.get('prize_blue', 0):02d}
💰 中奖: {latest_verification.get('total_prize', 0)}元
"""
        
        # 构建推送内容
        content = f"""🎯 双色球第{period}期AI智能预测

📊 单式推荐 (共{len(recommendations)}注)：
{rec_summary.strip()}
{complex_summary}
{verification_summary}
📈 分析要点：
• 基于机器学习LightGBM算法
• 结合历史频率和遗漏分析  
• 运用关联规则挖掘技术
• 多因子加权评分优选
{optuna_info}{backtest_info}
⏰ 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

💡 仅供参考，理性投注！祝您好运！"""
        
        return send_wxpusher_message(content, title)
        
    except Exception as e:
        logging.error(f"构建分析报告推送内容失败: {e}")
        return {"success": False, "error": f"内容构建失败: {str(e)}"}

def send_verification_report(verification_data: Dict) -> Dict:
    """发送双色球验证报告
    
    Args:
        verification_data: 验证报告数据字典，包含中奖信息
    
    Returns:
        推送结果字典
    """
    try:
        period = verification_data.get('eval_period', '未知')
        title = f"✅ 双色球第{period}期验证报告"
        
        winning_red = verification_data.get('prize_red', [])
        winning_blue = verification_data.get('prize_blue', 0)
        rec_prize = verification_data.get('rec_prize', 0)
        com_prize = verification_data.get('com_prize', 0)
        total_prize = verification_data.get('total_prize', 0)
        
        # 构建中奖统计
        rec_breakdown = verification_data.get('rec_breakdown', {})
        com_breakdown = verification_data.get('com_breakdown', {})
        
        rec_summary = "无中奖"
        if rec_prize > 0:
            rec_details = []
            for level, count in rec_breakdown.items():
                if count > 0:
                    rec_details.append(f"{level}等奖x{count}")
            rec_summary = ", ".join(rec_details) if rec_details else "中奖但无详情"
        
        com_summary = "无中奖"
        if com_prize > 0:
            com_details = []
            for level, count in com_breakdown.items():
                if count > 0:
                    com_details.append(f"{level}等奖x{count}")
            com_summary = ", ".join(com_details) if com_details else "中奖但无详情"
        
        # 计算总投注数
        rec_count = len(verification_data.get('rec_winners', []))
        com_count = len(verification_data.get('com_winners', []))
        total_bets = rec_count + com_count
        
        # 构建验证报告内容
        content = f"""✅ 双色球第{period}期开奖验证

🎱 开奖号码：
红球：{' '.join(f'{n:02d}' for n in winning_red)}
蓝球：{winning_blue:02d}

📊 验证结果：
单式推荐：{rec_summary}
复式推荐：{com_summary}
总奖金：{total_prize:,}元

💰 投资回报：
估算成本：{total_bets * 2:,}元（按单注2元计算）
收益：{total_prize - total_bets * 2:,}元
回报率：{((total_prize - total_bets * 2) / (total_bets * 2) * 100):.2f}%

⏰ 验证时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"""
        
        return send_wxpusher_message(content, title)
        
    except Exception as e:
        logging.error(f"构建验证报告推送内容失败: {e}")
        return {"success": False, "error": f"内容构建失败: {str(e)}"}

def send_error_notification(error_msg: str, script_name: str = "双色球系统") -> Dict:
    """发送错误通知
    
    Args:
        error_msg: 错误信息
        script_name: 脚本名称
    
    Returns:
        推送结果字典
    """
    title = f"⚠️ {script_name}运行异常"
    
    content = f"""⚠️ 系统运行异常通知

📍 异常位置：{script_name}
🕒 发生时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
❌ 错误信息：
{error_msg}

请及时检查系统状态！"""
    
    return send_wxpusher_message(content, title)

def send_daily_summary(analysis_success: bool, verification_success: bool, 
                      analysis_file: str = None, error_msg: str = None) -> Dict:
    """发送每日运行摘要
    
    Args:
        analysis_success: 分析是否成功
        verification_success: 验证是否成功
        analysis_file: 分析报告文件名
        error_msg: 错误信息（如有）
    
    Returns:
        推送结果字典
    """
    title = "📊 双色球系统日报"
    
    # 状态图标
    analysis_status = "✅" if analysis_success else "❌"
    verification_status = "✅" if verification_success else "❌"
    
    content = f"""📊 双色球AI预测系统日报

🕒 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}

📈 任务执行状态：
{analysis_status} 数据分析与预测
{verification_status} 历史验证计算

📁 生成文件："""
    
    if analysis_file:
        content += f"\n• {analysis_file}"
    
    if error_msg:
        content += f"\n\n⚠️ 异常信息：\n{error_msg}"
    
    content += "\n\n🔔 系统已自动完成定时任务"
    
    return send_wxpusher_message(content, title)

def send_complete_recommendations(period: int, recommendations: List[str], 
                                 complex_red: List[str] = None, complex_blue: List[str] = None) -> Dict:
    """发送完整的推荐号码列表（分批发送以避免字符限制）
    
    Args:
        period: 预测期号
        recommendations: 推荐号码列表
        complex_red: 复式红球列表
        complex_blue: 复式蓝球列表
    
    Returns:
        推送结果字典
    """
    try:
        # 获取最新验证结果
        latest_verification = get_latest_verification_result()
        
        # 构建验证结果摘要
        verification_summary = ""
        if latest_verification:
            verification_summary = f"""
📅 最新验证（第{latest_verification.get('eval_period', '未知')}期）：
🎱 开奖: 红球 {' '.join(f'{n:02d}' for n in latest_verification.get('prize_red', []))} 蓝球 {latest_verification.get('prize_blue', 0):02d}
💰 中奖: {latest_verification.get('total_prize', 0)}元
"""
        
        # 构建完整推荐内容
        content_parts = [f"🎯 双色球第{period}期完整推荐"]
        
        if verification_summary:
            content_parts.append(verification_summary.strip())
        
        content_parts.append("📊 全部15注单式推荐：")
        
        # 简化格式显示所有推荐号码
        rec_lines = []
        for i, rec in enumerate(recommendations):
            import re
            red_match = re.search(r'红球\s*\[([^\]]+)\]', rec)
            blue_match = re.search(r'蓝球\s*\[(\d+)\]', rec)
            
            if red_match and blue_match:
                # 保持红球号码之间的空格，确保格式统一
                red_nums_list = [x.strip() for x in red_match.group(1).split()]
                red_nums = ' '.join(f'{int(x):02d}' for x in red_nums_list if x.isdigit())
                blue_num = f'{int(blue_match.group(1)):02d}'
                rec_lines.append(f"{i+1:2d}. {red_nums} + {blue_num}")
            else:
                rec_lines.append(f"{i+1:2d}. {rec}")
        
        # 将推荐分成两部分显示（前8注和后7注）
        content_parts.append("前8注：")
        content_parts.extend(rec_lines[:8])
        content_parts.append("\n后7注：")
        content_parts.extend(rec_lines[8:])
        
        # 添加复式参考
        if complex_red and complex_blue:
            red_combinations = comb(len(complex_red), 6) if len(complex_red) >= 6 else 0
            total_combinations = red_combinations * len(complex_blue)
            
            content_parts.extend([
                "",
                "📦 复式参考：",
                f"红球({len(complex_red)}个): {' '.join(complex_red)}",
                f"蓝球({len(complex_blue)}个): {' '.join(complex_blue)}",
                f"💰 成本: {total_combinations * 2:,}元 ({total_combinations:,}注)"
            ])
        
        content_parts.extend([
            "",
            f"⏰ 生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "💡 仅供参考，理性投注！"
        ])
        
        # 合并所有内容
        full_content = '\n'.join(content_parts)
        
        title = f"🎯 双色球第{period}期完整推荐"
        
        return send_wxpusher_message(full_content, title)
        
    except Exception as e:
        logging.error(f"构建完整推荐推送内容失败: {e}")
        return {"success": False, "error": f"内容构建失败: {str(e)}"}

def test_wxpusher_connection() -> bool:
    """测试微信推送连接
    
    Returns:
        连接是否成功
    """
    test_content = f"🔧 双色球推送系统测试\n\n测试时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n如收到此消息，说明推送功能正常！"
    result = send_wxpusher_message(test_content, "🔧 推送测试")
    return result.get("success", False)

if __name__ == "__main__":
    # 测试推送功能
    print("正在测试双色球微信推送功能...")
    
    # 测试基本推送
    if test_wxpusher_connection():
        print("✅ 微信推送测试成功！")
        
        # 测试分析报告推送
        test_recommendations = [
            "注 1: 红球 [01 17 18 22 27 32] 蓝球 [15]",
            "注 2: 红球 [01 06 09 14 17 26] 蓝球 [11]",
            "注 3: 红球 [02 10 20 22 26 32] 蓝球 [16]",
            "注 4: 红球 [06 07 09 22 26 32] 蓝球 [15]",
            "注 5: 红球 [06 14 17 26 27 30] 蓝球 [16]",
            "注 6: 红球 [01 02 03 06 17 22] 蓝球 [01]",
            "注 7: 红球 [01 06 09 17 26 27] 蓝球 [15]",
            "注 8: 红球 [01 07 09 17 26 32] 蓝球 [15]",
            "注 9: 红球 [01 07 10 20 22 26] 蓝球 [11]",
            "注 10: 红球 [01 06 12 17 20 26] 蓝球 [16]",
            "注 11: 红球 [06 07 08 17 26 32] 蓝球 [15]",
            "注 12: 红球 [01 06 07 14 22 27] 蓝球 [06]",
            "注 13: 红球 [08 10 14 19 22 26] 蓝球 [15]",
            "注 14: 红球 [01 05 06 07 18 22] 蓝球 [01]",
            "注 15: 红球 [07 09 17 18 20 26] 蓝球 [16]"
        ]
        
        print("测试分析报告推送...")
        send_analysis_report(
            "测试报告内容", 
            2025071, 
            test_recommendations[:5],  # 摘要只显示前5注
            complex_red=["01", "02", "03", "04", "05", "06", "07"],
            complex_blue=["08", "09", "10"]
        )
        
        print("测试完整推荐推送...")
        send_complete_recommendations(
            2025071, 
            test_recommendations,  # 所有15注
            complex_red=["01", "02", "03", "04", "05", "06", "07"],
            complex_blue=["08", "09", "10"]
        )
        
        print("测试验证报告推送...")
        test_verification = {
            'eval_period': 2025070,
            'prize_red': [2, 3, 15, 21, 22, 33],
            'prize_blue': 6,
            'total_prize': 0,
            'rec_prize': 0,
            'com_prize': 0,
            'rec_breakdown': {},
            'com_breakdown': {},
            'rec_winners': [],
            'com_winners': []
        }
        send_verification_report(test_verification)
        
    else:
        print("❌ 微信推送测试失败！请检查配置。") 