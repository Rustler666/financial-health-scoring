"""
数据获取模块 - 使用akshare获取A股上市公司财务数据
"""
import akshare as ak
import pandas as pd
import numpy as np
import warnings
import time
warnings.filterwarnings('ignore')


def get_hs300_stocks():
    """获取沪深300成分股列表"""
    print("正在获取沪深300成分股列表...")
    try:
        df = ak.index_stock_cons_weight_csindex(symbol="000300")
        stocks = df[['成分券代码', '成分券名称', '交易所']].copy()
        stocks.columns = ['stock_code', 'stock_name', 'exchange']
        stocks['stock_code'] = stocks['stock_code'].astype(str).str.zfill(6)
        print(f"成功获取 {len(stocks)} 只沪深300成分股")
        return stocks
    except Exception as e:
        print(f"获取沪深300成分股失败: {e}")
        return pd.DataFrame()


def get_stock_industry(stock_codes):
    """获取股票所属行业（通过业绩报表批量获取）"""
    print("正在批量获取行业分类数据...")
    try:
        yjbb = ak.stock_yjbb_em(date="20241231")
        yjbb['股票代码'] = yjbb['股票代码'].astype(str).str.zfill(6)
        industry_map = dict(zip(yjbb['股票代码'], yjbb['所处行业']))
        return industry_map
    except Exception as e:
        print(f"批量获取行业分类失败: {e}")
        return {}


def get_financial_indicators_for_stock(stock_code, stock_name=""):
    """
    使用 stock_financial_analysis_indicator 获取单只股票的财务指标
    返回最新报告期的关键指标
    """
    try:
        df = ak.stock_financial_analysis_indicator(symbol=stock_code, start_year="2023")
        if df.empty:
            return None
        latest = df.iloc[0]
        result = {
            'stock_code': stock_code,
            'stock_name': stock_name,
            'report_date': latest['日期'],
            'roe': latest.get('净资产收益率(%)', np.nan),
            'debt_ratio': latest.get('资产负债率(%)', np.nan),
            'current_ratio': latest.get('流动比率', np.nan),
            'revenue_growth': latest.get('主营业务收入增长率(%)', np.nan),
        }
        for key in ['roe', 'debt_ratio', 'current_ratio', 'revenue_growth']:
            val = result[key]
            if pd.isna(val):
                continue
            if isinstance(val, str):
                val = val.replace('%', '').strip()
                if val == '' or val == '--':
                    result[key] = np.nan
                    continue
            try:
                result[key] = float(val)
            except (ValueError, TypeError):
                result[key] = np.nan
        return result
    except Exception as e:
        return None


def get_financial_data(stock_codes, stock_names=None, max_stocks=100):
    """
    获取指定股票的财务指标数据
    指标：ROE、资产负债率、流动比率、营业收入同比增长率
    """
    stock_codes = stock_codes[:max_stocks]
    if stock_names is None:
        stock_names = [''] * len(stock_codes)
    
    print(f"正在获取 {len(stock_codes)} 只股票的财务指标数据...")
    financial_data = []
    failed_count = 0
    
    for i, (code, name) in enumerate(zip(stock_codes, stock_names)):
        if i % 10 == 0:
            print(f"  进度: {i}/{len(stock_codes)} (成功: {len(financial_data)}, 失败: {failed_count})")
        result = get_financial_indicators_for_stock(code, name)
        if result:
            financial_data.append(result)
        else:
            failed_count += 1
        time.sleep(0.15)
    
    result_df = pd.DataFrame(financial_data)
    if result_df.empty:
        print("警告: 未能获取任何财务数据")
        return result_df
    
    industry_map = get_stock_industry(stock_codes)
    result_df['industry'] = result_df['stock_code'].map(industry_map)
    result_df['industry'] = result_df['industry'].fillna('其他')
    
    print(f"\n数据获取完成: 成功 {len(financial_data)} 只, 失败 {failed_count} 只")
    valid_count = result_df[['roe', 'debt_ratio', 'current_ratio', 'revenue_growth']].notna().sum()
    print("各指标有效数据量:")
    for col, count in valid_count.items():
        print(f"  {col}: {count}/{len(result_df)} ({count/len(result_df)*100:.1f}%)")
    return result_df


def save_raw_data(df, filepath='data/raw_financial_data.csv'):
    """保存原始数据到CSV"""
    df.to_csv(filepath, index=False, encoding='utf-8-sig')
    print(f"原始数据已保存到: {filepath}")


def load_raw_data(filepath='data/raw_financial_data.csv'):
    """从CSV加载原始数据"""
    return pd.read_csv(filepath, encoding='utf-8-sig')


if __name__ == '__main__':
    hs300 = get_hs300_stocks()
    if not hs300.empty:
        stock_codes = hs300['stock_code'].tolist()
        stock_names = hs300['stock_name'].tolist()
        fin_data = get_financial_data(stock_codes, stock_names, max_stocks=100)
        save_raw_data(fin_data)
        print(f"\n数据预览:")
        print(fin_data.head(10).to_string())
    else:
        print("获取股票列表失败")
