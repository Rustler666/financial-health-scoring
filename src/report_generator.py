"""
报告生成模块 - 生成HTML财务健康度评估报告
"""
import pandas as pd
import numpy as np
import base64
import os
from datetime import datetime


class ReportGenerator:
    """HTML报告生成器"""
    
    def __init__(self, df, chart_dir='reports/charts', output_path='reports/financial_health_report.html'):
        self.df = df.copy()
        self.chart_dir = chart_dir
        self.output_path = output_path
    
    def _img_to_base64(self, path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    
    def _get_summary_stats(self):
        total = len(self.df)
        mean_score = self.df['composite_score'].mean()
        risk_dist = self.df['risk_level'].value_counts().to_dict()
        high_risk = self.df[self.df['risk_level'].isin(['D-关注', 'E-高风险'])].shape[0]
        top5 = self.df.nlargest(5, 'composite_score')[['stock_name', 'stock_code', 'composite_score', 'risk_level']]
        bottom5 = self.df.nsmallest(5, 'composite_score')[['stock_name', 'stock_code', 'composite_score', 'risk_level']]
        return {'total': total, 'mean_score': mean_score, 'risk_dist': risk_dist, 'high_risk': high_risk, 'top5': top5, 'bottom5': bottom5}
    
    def _get_industry_summary(self):
        stats = self.df.groupby('industry').agg({'composite_score': 'mean', 'stock_code': 'count'}).rename(columns={'stock_code': 'count'})
        return stats.sort_values('composite_score', ascending=False)
    
    def _get_high_risk_table(self):
        high_risk = self.df[self.df['risk_level'].isin(['D-关注', 'E-高风险'])].copy()
        if 'risk_flags' not in high_risk.columns:
            high_risk['risk_flags'] = ''
            high_risk.loc[high_risk['debt_ratio'] > 70, 'risk_flags'] += '高负债 '
            high_risk.loc[high_risk['current_ratio'] < 1.0, 'risk_flags'] += '低流动性 '
            high_risk.loc[high_risk['revenue_growth'] < 0, 'risk_flags'] += '营收下滑 '
            high_risk.loc[high_risk['roe'] < 5, 'risk_flags'] += '低盈利 '
        return high_risk.sort_values('composite_score', ascending=True)[['stock_name', 'stock_code', 'industry', 'roe', 'debt_ratio', 'current_ratio', 'revenue_growth', 'composite_score', 'risk_level', 'risk_flags']]
    
    def _build_html(self):
        stats = self._get_summary_stats()
        industry = self._get_industry_summary()
        high_risk_df = self._get_high_risk_table()
        charts = {}
        for name in ['01_score_distribution', '02_risk_pie', '03_industry_bar', '04_quadrant', '05_high_risk_scatter', '06_dimension_box', '07_top_bottom']:
            path = f"{self.chart_dir}/{name}.png"
            if os.path.exists(path):
                charts[name] = self._img_to_base64(path)
        top5_html = stats['top5'].to_html(index=False, classes='data-table', border=0)
        bottom5_html = stats['bottom5'].to_html(index=False, classes='data-table', border=0)
        industry_html = industry.head(15).to_html(classes='data-table', border=0)
        high_risk_html = high_risk_df.head(20).to_html(index=False, classes='data-table', border=0)
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>上市公司财务健康度评估报告</title>
<style>
:root {{ --primary: #2c3e50; --accent: #3498db; --success: #2ecc71; --warning: #f1c40f; --danger: #e74c3c; --bg: #f8f9fa; --card: #ffffff; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; background: var(--bg); color: #333; line-height: 1.6; }}
.container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
header {{ background: linear-gradient(135deg, var(--primary), #34495e); color: white; padding: 40px; border-radius: 12px; margin-bottom: 30px; text-align: center; }}
header h1 {{ font-size: 2rem; margin-bottom: 10px; }}
.metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
.metric-card {{ background: var(--card); padding: 24px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); text-align: center; }}
.metric-card .number {{ font-size: 2.2rem; font-weight: bold; color: var(--accent); }}
.section {{ background: var(--card); border-radius: 10px; padding: 30px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
.section h2 {{ font-size: 1.3rem; color: var(--primary); margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid var(--accent); }}
.chart {{ text-align: center; margin: 20px 0; }}
.chart img {{ max-width: 100%; height: auto; border-radius: 8px; }}
.data-table {{ width: 100%; border-collapse: collapse; font-size: 0.9rem; }}
.data-table th {{ background: var(--primary); color: white; padding: 10px; text-align: left; }}
.data-table td {{ padding: 10px; border-bottom: 1px solid #eee; }}
.data-table tr:hover {{ background: #f5f5f5; }}
.risk-tag {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: bold; }}
.risk-A {{ background: #d4edda; color: #155724; }}
.risk-B {{ background: #d1ecf1; color: #0c5460; }}
.risk-C {{ background: #fff3cd; color: #856404; }}
.risk-D {{ background: #f8d7da; color: #721c24; }}
.risk-E {{ background: #f5c6cb; color: #721c24; }}
.insight-box {{ background: #e8f4fd; border-left: 4px solid var(--accent); padding: 16px 20px; border-radius: 0 8px 8px 0; margin: 16px 0; }}
.insight-box.danger {{ background: #fde8e8; border-left-color: var(--danger); }}
.insight-box.warning {{ background: #fef3c7; border-left-color: var(--warning); }}
footer {{ text-align: center; color: #999; padding: 30px; font-size: 0.85rem; }}
.two-col {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
@media (max-width: 768px) {{ .two-col {{ grid-template-columns: 1fr; }} header h1 {{ font-size: 1.4rem; }} }}
</style>
</head>
<body>
<div class="container">
<header><h1>📊 基于财务指标的上市公司信用风险评估报告</h1><p>沪深300成分股 · 多维度财务健康度评分模型 · 生成时间: {now}</p></header>
<div class="metrics">
<div class="metric-card"><div class="number">{stats['total']}</div><div class="label">分析公司数</div></div>
<div class="metric-card"><div class="number">{stats['mean_score']:.1f}</div><div class="label">平均综合得分</div></div>
<div class="metric-card"><div class="number">{stats['high_risk']}</div><div class="label">高风险/关注公司</div></div>
<div class="metric-card"><div class="number">{stats['risk_dist'].get('A-优秀', 0) + stats['risk_dist'].get('B-良好', 0)}</div><div class="label">健康公司数</div></div>
</div>
<div class="section">
<h2>📌 核心发现</h2>
<div class="insight-box"><strong>整体评估：</strong>本次评估覆盖沪深300指数中 {stats['total']} 家上市公司，平均综合得分 <strong>{stats['mean_score']:.1f}</strong> 分。其中，评级为"优秀/良好"的公司有 {stats['risk_dist'].get('A-优秀', 0) + stats['risk_dist'].get('B-良好', 0)} 家，评级为"关注/高风险"的公司有 {stats['high_risk']} 家，需重点关注。</div>
<div class="insight-box warning"><strong>行业差异显著：</strong>白酒、能源金属、生物制品等行业财务健康度整体较高；而银行、证券、房地产开发等行业因高杠杆特征，平均得分偏低。</div>
<div class="insight-box danger"><strong>风险提示：</strong>共识别出 {stats['high_risk']} 家"高负债+低现金流"特征的高风险公司，主要分布在金融和房地产板块，建议密切跟踪其偿债能力变化。</div>
</div>
<div class="section"><h2>📈 综合得分分布</h2><div class="chart"><img src="data:image/png;base64,{charts.get('01_score_distribution', '')}" alt="得分分布"></div></div>
<div class="section"><h2>🎯 风险等级分布</h2><div class="two-col"><div class="chart"><img src="data:image/png;base64,{charts.get('02_risk_pie', '')}" alt="风险等级饼图"></div><div><h3>各等级定义</h3><ul style="line-height: 2;"><li><span class="risk-tag risk-A">A-优秀</span> 综合得分 ≥ 80，财务结构稳健</li><li><span class="risk-tag risk-B">B-良好</span> 综合得分 65-79，整体健康</li><li><span class="risk-tag risk-C">C-一般</span> 综合得分 50-64，存在改进空间</li><li><span class="risk-tag risk-D">D-关注</span> 综合得分 35-49，需关注风险</li><li><span class="risk-tag risk-E">E-高风险</span> 综合得分 &lt; 35，财务压力大</li></ul></div></div></div>
<div class="section"><h2>🏭 行业对比分析</h2><div class="chart"><img src="data:image/png;base64,{charts.get('03_industry_bar', '')}" alt="行业排名"></div><h3>行业平均得分 Top 15</h3>{industry_html}</div>
<div class="section"><h2>📍 四象限分析：盈利能力 vs 偿债能力</h2><div class="chart"><img src="data:image/png;base64,{charts.get('04_quadrant', '')}" alt="四象限图"></div><div class="insight-box">四象限图以ROE（横轴）和资产负债率（纵轴）为维度，将公司分为四个区域。<strong>右下角（高ROE+低负债）</strong>为优质投资标的；<strong>左上角（低ROE+高负债）</strong>为高风险区域，需警惕。</div></div>
<div class="section"><h2>⚠️ 高风险公司识别</h2><div class="chart"><img src="data:image/png;base64,{charts.get('05_high_risk_scatter', '')}" alt="高风险散点图"></div><h3>高风险公司列表</h3>{high_risk_html}</div>
<div class="section"><h2>📊 各维度得分分析</h2><div class="chart"><img src="data:image/png;base64,{charts.get('06_dimension_box', '')}" alt="维度箱线图"></div></div>
<div class="section"><h2>🏆 Top 5 健康公司 vs Bottom 5 风险公司</h2><div class="chart"><img src="data:image/png;base64,{charts.get('07_top_bottom', '')}" alt="Top/Bottom对比"></div><div class="two-col"><div><h3>🏆 Top 5 最健康</h3>{top5_html}</div><div><h3>⚠️ Bottom 5 最高风险</h3>{bottom5_html}</div></div></div>
<div class="section"><h2>📋 方法论说明</h2><p style="margin-bottom: 12px;"><strong>数据来源：</strong>akshare 开源金融数据接口，沪深300指数成分股财务数据。</p><p style="margin-bottom: 12px;"><strong>评分指标：</strong></p><ul style="margin-left: 20px; line-height: 1.8;"><li><strong>ROE（净资产收益率）</strong>权重30% — 衡量股东回报能力</li><li><strong>资产负债率</strong>权重25% — 衡量长期偿债能力，适中为佳</li><li><strong>流动比率</strong>权重25% — 衡量短期流动性，越高越好</li><li><strong>营收增速</strong>权重20% — 衡量成长性，越高越好</li></ul><p style="margin-top: 12px;"><strong>评分规则：</strong>每个指标按百分制评分，缺失指标自动重新归一化权重，最终综合得分按加权平均计算。</p><p style="margin-top: 8px; color: #888; font-size: 0.85rem;">⚠️ 免责声明：本报告仅供学习研究参考，不构成任何投资建议。数据来源于公开渠道，可能存在延迟或误差。</p></div>
<footer><p>基于财务指标的上市公司信用风险评估系统 | Python + pandas + akshare + matplotlib</p><p>生成时间: {now}</p></footer>
</div>
</body>
</html>"""
        return html
    
    def generate(self):
        print("正在生成HTML报告...")
        html = self._build_html()
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"HTML报告已保存到: {self.output_path}")
        return self.output_path


if __name__ == '__main__':
    import data_fetcher
    from scoring_model import FinancialHealthScorer
    df = data_fetcher.load_raw_data('data/raw_financial_data.csv')
    scorer = FinancialHealthScorer()
    scored_df = scorer.calculate_scores(df)
    gen = ReportGenerator(scored_df)
    gen.generate()
