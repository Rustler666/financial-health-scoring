"""
主程序 - 上市公司财务健康度评估系统
完整流程：数据获取 → 评分计算 → 可视化 → 报告生成
"""
import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_fetcher import get_hs300_stocks, get_financial_data, save_raw_data, load_raw_data
from src.scoring_model import FinancialHealthScorer
from src.visualizer import FinancialVisualizer
from src.report_generator import ReportGenerator


def main():
    print("=" * 60)
    print("  上市公司财务健康度评估系统")
    print("  Financial Health Scoring System for Listed Companies")
    print("=" * 60)
    
    # 步骤1: 数据获取
    print("\n【步骤1】数据获取")
    print("-" * 40)
    
    raw_data_path = 'data/raw_financial_data.csv'
    scored_data_path = 'data/scored_financial_data.csv'
    
    if os.path.exists(raw_data_path):
        print(f"检测到已存在数据文件: {raw_data_path}")
        use_existing = input("是否使用已有数据? [Y/n]: ").strip().lower()
        if use_existing in ('', 'y', 'yes'):
            df = load_raw_data(raw_data_path)
            print(f"已加载 {len(df)} 条记录")
        else:
            df = fetch_new_data()
    else:
        df = fetch_new_data()
    
    # 步骤2: 评分计算
    print("\n【步骤2】财务健康度评分")
    print("-" * 40)
    
    if os.path.exists(scored_data_path):
        print(f"检测到已存在评分结果: {scored_data_path}")
        use_existing = input("是否使用已有评分? [Y/n]: ").strip().lower()
        if use_existing in ('', 'y', 'yes'):
            import pandas as pd
            scored_df = pd.read_csv(scored_data_path, encoding='utf-8-sig')
        else:
            scored_df = calculate_scores(df)
    else:
        scored_df = calculate_scores(df)
    
    # 步骤3: 可视化
    print("\n【步骤3】生成可视化图表")
    print("-" * 40)
    viz = FinancialVisualizer(scored_df, output_dir='reports/charts')
    chart_paths = viz.generate_all()
    print(f"图表已保存到 reports/charts/ 目录")
    
    # 步骤4: 生成报告
    print("\n【步骤4】生成HTML报告")
    print("-" * 40)
    gen = ReportGenerator(scored_df, chart_dir='reports/charts', 
                           output_path='reports/financial_health_report.html')
    report_path = gen.generate()
    
    # 完成
    print("\n" + "=" * 60)
    print("  ✅ 评估流程全部完成!")
    print("=" * 60)
    print(f"\n📁 输出文件:")
    print(f"   - 原始数据:    data/raw_financial_data.csv")
    print(f"   - 评分结果:    data/scored_financial_data.csv")
    print(f"   - 可视化图表:  reports/charts/ (共 {len(chart_paths)} 张)")
    print(f"   - HTML报告:    {report_path}")
    print(f"\n💡 请用浏览器打开 {report_path} 查看完整报告")


def fetch_new_data():
    """获取新数据"""
    hs300 = get_hs300_stocks()
    if hs300.empty:
        print("错误: 无法获取股票列表")
        sys.exit(1)
    
    stock_codes = hs300['stock_code'].tolist()
    stock_names = hs300['stock_name'].tolist()
    df = get_financial_data(stock_codes, stock_names, max_stocks=100)
    
    if df.empty:
        print("错误: 未能获取任何财务数据")
        sys.exit(1)
    
    save_raw_data(df)
    return df


def calculate_scores(df):
    """计算评分"""
    scorer = FinancialHealthScorer()
    scored_df = scorer.calculate_scores(df)
    
    print(f"\n评分统计:")
    print(f"  - 平均综合得分: {scored_df['composite_score'].mean():.2f}")
    print(f"  - 最高得分:     {scored_df['composite_score'].max():.2f}")
    print(f"  - 最低得分:     {scored_df['composite_score'].min():.2f}")
    print(f"\n风险等级分布:")
    for level, count in scored_df['risk_level'].value_counts().items():
        print(f"  - {level}: {count} 家")
    
    scored_df.to_csv('data/scored_financial_data.csv', index=False, encoding='utf-8-sig')
    print("\n评分结果已保存")
    return scored_df


if __name__ == '__main__':
    # 自动模式：跳过交互，直接使用已有数据
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        print("自动模式运行中...")
        df = load_raw_data('data/raw_financial_data.csv')
        scorer = FinancialHealthScorer()
        scored_df = scorer.calculate_scores(df)
        viz = FinancialVisualizer(scored_df, output_dir='reports/charts')
        viz.generate_all()
        gen = ReportGenerator(scored_df, chart_dir='reports/charts',
                               output_path='reports/financial_health_report.html')
        gen.generate()
        print("\n✅ 自动模式完成!")
    else:
        main()
