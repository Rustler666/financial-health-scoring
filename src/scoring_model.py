"""
评分模型模块 - 构建财务健康度评分卡
"""
import pandas as pd
import numpy as np


class FinancialHealthScorer:
    """
    财务健康度评分模型
    
    评分维度：
    1. 盈利能力（ROE）- 权重30%
    2. 偿债能力（资产负债率）- 权重25%
    3. 流动性（流动比率）- 权重25%
    4. 成长能力（营收增速）- 权重20%
    """
    
    def __init__(self):
        self.weights = {
            'roe': 0.30,
            'debt_ratio': 0.25,
            'current_ratio': 0.25,
            'revenue_growth': 0.20
        }
        self.thresholds = {
            'roe': {'excellent': 20, 'good': 15, 'average': 10, 'poor': 5, 'bad': 0},
            'debt_ratio': {'excellent': 40, 'good': 50, 'average': 60, 'poor': 70, 'bad': 100},
            'current_ratio': {'excellent': 2.0, 'good': 1.5, 'average': 1.0, 'poor': 0.8, 'bad': 0},
            'revenue_growth': {'excellent': 30, 'good': 20, 'average': 10, 'poor': 0, 'bad': -100}
        }
    
    def _score_roe(self, value):
        if pd.isna(value):
            return np.nan
        t = self.thresholds['roe']
        if value >= t['excellent']:
            return min(100, 90 + (value - t['excellent']) * 1)
        elif value >= t['good']:
            return 75 + (value - t['good']) / (t['excellent'] - t['good']) * 14
        elif value >= t['average']:
            return 60 + (value - t['average']) / (t['good'] - t['average']) * 14
        elif value >= t['poor']:
            return 40 + (value - t['poor']) / (t['average'] - t['poor']) * 19
        else:
            return max(0, value / t['poor'] * 40)
    
    def _score_debt_ratio(self, value):
        if pd.isna(value):
            return np.nan
        t = self.thresholds['debt_ratio']
        if value <= t['excellent']:
            return 95
        elif value <= t['good']:
            return 90 - (value - t['excellent']) / (t['good'] - t['excellent']) * 5
        elif value <= t['average']:
            return 75 - (value - t['good']) / (t['average'] - t['good']) * 15
        elif value <= t['poor']:
            return 60 - (value - t['average']) / (t['poor'] - t['average']) * 20
        elif value <= t['bad']:
            return 40 - (value - t['poor']) / (t['bad'] - t['poor']) * 40
        else:
            return max(0, 40 - (value - 70) * 2)
    
    def _score_current_ratio(self, value):
        if pd.isna(value):
            return np.nan
        t = self.thresholds['current_ratio']
        if value >= t['excellent']:
            return min(100, 90 + (value - t['excellent']) * 5)
        elif value >= t['good']:
            return 75 + (value - t['good']) / (t['excellent'] - t['good']) * 14
        elif value >= t['average']:
            return 60 + (value - t['average']) / (t['good'] - t['average']) * 14
        elif value >= t['poor']:
            return 40 + (value - t['poor']) / (t['average'] - t['poor']) * 19
        else:
            return max(0, value / t['poor'] * 40)
    
    def _score_revenue_growth(self, value):
        if pd.isna(value):
            return np.nan
        t = self.thresholds['revenue_growth']
        if value >= t['excellent']:
            return min(100, 90 + (value - t['excellent']) * 0.5)
        elif value >= t['good']:
            return 75 + (value - t['good']) / (t['excellent'] - t['good']) * 14
        elif value >= t['average']:
            return 60 + (value - t['average']) / (t['good'] - t['average']) * 14
        elif value >= t['poor']:
            return 40 + (value - t['poor']) / (t['average'] - t['poor']) * 19
        else:
            return max(0, 40 + value / abs(t['bad']) * 40)
    
    def calculate_scores(self, df):
        result = df.copy()
        result['roe_score'] = result['roe'].apply(self._score_roe)
        result['debt_score'] = result['debt_ratio'].apply(self._score_debt_ratio)
        result['liquidity_score'] = result['current_ratio'].apply(self._score_current_ratio)
        result['growth_score'] = result['revenue_growth'].apply(self._score_revenue_growth)
        
        score_cols = ['roe_score', 'debt_score', 'liquidity_score', 'growth_score']
        weights = [self.weights['roe'], self.weights['debt_ratio'],
                   self.weights['current_ratio'], self.weights['revenue_growth']]
        
        def weighted_score(row):
            valid_scores, valid_weights = [], []
            for col, w in zip(score_cols, weights):
                if pd.notna(row[col]):
                    valid_scores.append(row[col])
                    valid_weights.append(w)
            if not valid_scores:
                return np.nan
            total_w = sum(valid_weights)
            return sum(s * w / total_w for s, w in zip(valid_scores, valid_weights))
        
        result['composite_score'] = result.apply(weighted_score, axis=1)
        
        def risk_level(score):
            if pd.isna(score):
                return '未知'
            elif score >= 80:
                return 'A-优秀'
            elif score >= 65:
                return 'B-良好'
            elif score >= 50:
                return 'C-一般'
            elif score >= 35:
                return 'D-关注'
            else:
                return 'E-高风险'
        
        result['risk_level'] = result['composite_score'].apply(risk_level)
        return result
    
    def identify_high_risk(self, df, top_n=15):
        high_debt = df['debt_ratio'] > 70
        low_liquidity = df['current_ratio'] < 1.0
        negative_growth = df['revenue_growth'] < 0
        low_roe = df['roe'] < 5
        
        df = df.copy()
        df['risk_flags'] = ''
        df.loc[high_debt, 'risk_flags'] += '高负债;'
        df.loc[low_liquidity, 'risk_flags'] += '低流动性;'
        df.loc[negative_growth, 'risk_flags'] += '营收下滑;'
        df.loc[low_roe, 'risk_flags'] += '低盈利;'
        df['risk_count'] = high_debt.astype(int) + low_liquidity.astype(int) + negative_growth.astype(int) + low_roe.astype(int)
        
        high_risk = df[df['risk_count'] >= 2].copy()
        return high_risk.sort_values('composite_score', ascending=True).head(top_n)
    
    def industry_analysis(self, df):
        industry_stats = df.groupby('industry').agg({
            'roe': 'mean',
            'debt_ratio': 'mean',
            'current_ratio': 'mean',
            'revenue_growth': 'mean',
            'composite_score': 'mean',
            'stock_code': 'count'
        }).rename(columns={'stock_code': 'company_count'})
        return industry_stats.sort_values('composite_score', ascending=False).round(2)


if __name__ == '__main__':
    import data_fetcher
    fin_data = data_fetcher.load_raw_data('data/raw_financial_data.csv')
    print(f"加载了 {len(fin_data)} 条记录")
    
    scorer = FinancialHealthScorer()
    scored_df = scorer.calculate_scores(fin_data)
    
    print("\n=== 评分结果预览（Top 15）===")
    cols = ['stock_code', 'stock_name', 'industry', 'roe', 'debt_ratio', 'current_ratio', 'revenue_growth', 'composite_score', 'risk_level']
    print(scored_df[cols].head(15).to_string())
    
    print("\n=== 高风险公司（Top 10）===")
    print(scorer.identify_high_risk(scored_df).head(10).to_string())
    
    print("\n=== 行业排名 ===")
    print(scorer.industry_analysis(scored_df).to_string())
    
    scored_df.to_csv('data/scored_financial_data.csv', index=False, encoding='utf-8-sig')
    print("\n评分结果已保存到: data/scored_financial_data.csv")
