"""
可视化模块 - 生成财务健康度分析图表
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class FinancialVisualizer:
    """财务健康度可视化器"""
    
    def __init__(self, df, output_dir='reports/charts'):
        self.df = df.copy()
        self.output_dir = output_dir
        import os
        os.makedirs(output_dir, exist_ok=True)
    
    def _save(self, name):
        path = f"{self.output_dir}/{name}.png"
        plt.tight_layout()
        plt.savefig(path, dpi=150, bbox_inches='tight')
        plt.close()
        return path
    
    def plot_score_distribution(self):
        """综合得分分布直方图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        scores = self.df['composite_score'].dropna()
        ax.hist(scores, bins=20, color='#4A90D9', edgecolor='white', alpha=0.8)
        ax.axvline(scores.mean(), color='red', linestyle='--', linewidth=2, label=f'平均分: {scores.mean():.1f}')
        ax.set_xlabel('综合得分', fontsize=12)
        ax.set_ylabel('公司数量', fontsize=12)
        ax.set_title('沪深300成分股财务健康度综合得分分布', fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        return self._save('01_score_distribution')
    
    def plot_risk_pie(self):
        """风险等级饼图"""
        fig, ax = plt.subplots(figsize=(8, 8))
        risk_counts = self.df['risk_level'].value_counts()
        colors = {'A-优秀': '#2ecc71', 'B-良好': '#3498db', 'C-一般': '#f1c40f',
                  'D-关注': '#e67e22', 'E-高风险': '#e74c3c', '未知': '#95a5a6'}
        pie_colors = [colors.get(r, '#95a5a6') for r in risk_counts.index]
        ax.pie(risk_counts, labels=risk_counts.index, autopct='%1.1f%%', colors=pie_colors,
               startangle=90, textprops={'fontsize': 11})
        ax.set_title('财务健康风险等级分布', fontsize=14, fontweight='bold')
        return self._save('02_risk_pie')
    
    def plot_industry_bar(self, top_n=15):
        """行业平均得分柱状图"""
        industry_stats = self.df.groupby('industry').agg({
            'composite_score': 'mean', 'stock_code': 'count'
        }).rename(columns={'stock_code': 'count'})
        industry_stats = industry_stats[industry_stats['count'] >= 1].sort_values('composite_score', ascending=True)
        
        fig, ax = plt.subplots(figsize=(10, max(6, len(industry_stats) * 0.35)))
        colors = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(industry_stats)))
        ax.barh(range(len(industry_stats)), industry_stats['composite_score'], color=colors)
        ax.set_yticks(range(len(industry_stats)))
        ax.set_yticklabels([f"{idx} (n={int(row['count'])})" for idx, row in industry_stats.iterrows()], fontsize=9)
        ax.set_xlabel('平均综合得分', fontsize=12)
        ax.set_title('各行业财务健康度平均得分排名', fontsize=14, fontweight='bold')
        ax.axvline(60, color='red', linestyle='--', alpha=0.5, label='及格线(60)')
        ax.legend(fontsize=10)
        ax.grid(axis='x', alpha=0.3)
        return self._save('03_industry_bar')
    
    def plot_quadrant(self):
        """四象限图：ROE vs 资产负债率"""
        fig, ax = plt.subplots(figsize=(10, 8))
        df_plot = self.df.dropna(subset=['roe', 'debt_ratio', 'composite_score'])
        scatter = ax.scatter(df_plot['roe'], df_plot['debt_ratio'],
                            c=df_plot['composite_score'], cmap='RdYlGn',
                            s=80, alpha=0.7, edgecolors='white', linewidth=0.5)
        ax.axhline(60, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(10, color='gray', linestyle='--', alpha=0.5)
        ax.text(15, 40, '优质区\n高ROE + 低负债', fontsize=10, ha='center', color='green', fontweight='bold')
        ax.text(5, 40, '低效区\n低ROE + 低负债', fontsize=10, ha='center', color='orange', fontweight='bold')
        ax.text(15, 80, '杠杆区\n高ROE + 高负债', fontsize=10, ha='center', color='blue', fontweight='bold')
        ax.text(5, 80, '危险区\n低ROE + 高负债', fontsize=10, ha='center', color='red', fontweight='bold')
        plt.colorbar(scatter, label='综合得分')
        ax.set_xlabel('净资产收益率 ROE (%)', fontsize=12)
        ax.set_ylabel('资产负债率 (%)', fontsize=12)
        ax.set_title('ROE-资产负债率四象限分析图', fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3)
        return self._save('04_quadrant')
    
    def plot_high_risk_scatter(self):
        """高风险公司散点图"""
        fig, ax = plt.subplots(figsize=(10, 7))
        df_plot = self.df.dropna(subset=['debt_ratio', 'current_ratio'])
        normal = df_plot[df_plot['debt_ratio'] <= 70]
        ax.scatter(normal['debt_ratio'], normal['current_ratio'],
                  c='#3498db', s=60, alpha=0.5, label='正常公司', edgecolors='white')
        high_risk = df_plot[df_plot['debt_ratio'] > 70]
        if len(high_risk) > 0:
            ax.scatter(high_risk['debt_ratio'], high_risk['current_ratio'],
                      c='#e74c3c', s=100, alpha=0.8, label='高负债公司', edgecolors='white', marker='X')
            for _, row in high_risk.iterrows():
                ax.annotate(row['stock_name'], (row['debt_ratio'], row['current_ratio']),
                           fontsize=8, xytext=(5, 5), textcoords='offset points')
        ax.axvline(70, color='red', linestyle='--', alpha=0.5, label='警戒线(70%)')
        ax.axhline(1.0, color='orange', linestyle='--', alpha=0.5, label='流动比率安全线(1.0)')
        ax.set_xlabel('资产负债率 (%)', fontsize=12)
        ax.set_ylabel('流动比率', fontsize=12)
        ax.set_title('高风险公司识别：高负债 + 低流动性', fontsize=14, fontweight='bold')
        ax.legend(fontsize=10)
        ax.grid(alpha=0.3)
        return self._save('05_high_risk_scatter')
    
    def plot_dimension_box(self):
        """各维度得分箱线图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        score_data = [
            self.df['roe_score'].dropna(), self.df['debt_score'].dropna(),
            self.df['liquidity_score'].dropna(), self.df['growth_score'].dropna()
        ]
        labels = ['盈利能力\n(ROE)', '偿债能力\n(资产负债率)', '流动性\n(流动比率)', '成长性\n(营收增速)']
        ax.boxplot(score_data, labels=labels, patch_artist=True,
                   boxprops=dict(facecolor='#4A90D9', alpha=0.7),
                   medianprops=dict(color='red', linewidth=2))
        ax.set_ylabel('得分', fontsize=12)
        ax.set_title('各维度得分分布箱线图', fontsize=14, fontweight='bold')
        ax.axhline(60, color='green', linestyle='--', alpha=0.5, label='及格线')
        ax.legend(fontsize=10)
        ax.grid(axis='y', alpha=0.3)
        return self._save('06_dimension_box')
    
    def plot_top_bottom(self, n=10):
        """Top N 和 Bottom N 对比"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        top = self.df.nlargest(n, 'composite_score')
        bottom = self.df.nsmallest(n, 'composite_score')
        ax1.barh(range(n), top['composite_score'].values[::-1], color='#2ecc71', alpha=0.8)
        ax1.set_yticks(range(n))
        ax1.set_yticklabels([f"{r['stock_name']} ({r['stock_code']})" for _, r in top.iloc[::-1].iterrows()], fontsize=9)
        ax1.set_xlabel('综合得分', fontsize=11)
        ax1.set_title(f'Top {n} 健康公司', fontsize=13, fontweight='bold')
        ax1.grid(axis='x', alpha=0.3)
        ax2.barh(range(n), bottom['composite_score'].values[::-1], color='#e74c3c', alpha=0.8)
        ax2.set_yticks(range(n))
        ax2.set_yticklabels([f"{r['stock_name']} ({r['stock_code']})" for _, r in bottom.iloc[::-1].iterrows()], fontsize=9)
        ax2.set_xlabel('综合得分', fontsize=11)
        ax2.set_title(f'Bottom {n} 风险公司', fontsize=13, fontweight='bold')
        ax2.grid(axis='x', alpha=0.3)
        plt.tight_layout()
        return self._save('07_top_bottom')
    
    def generate_all(self):
        """生成所有图表"""
        print("正在生成可视化图表...")
        paths = []
        paths.append(self.plot_score_distribution())
        paths.append(self.plot_risk_pie())
        paths.append(self.plot_industry_bar())
        paths.append(self.plot_quadrant())
        paths.append(self.plot_high_risk_scatter())
        paths.append(self.plot_dimension_box())
        paths.append(self.plot_top_bottom())
        print(f"已生成 {len(paths)} 张图表")
        return paths


if __name__ == '__main__':
    import data_fetcher
    from scoring_model import FinancialHealthScorer
    df = data_fetcher.load_raw_data('data/raw_financial_data.csv')
    scorer = FinancialHealthScorer()
    scored_df = scorer.calculate_scores(df)
    viz = FinancialVisualizer(scored_df)
    viz.generate_all()
