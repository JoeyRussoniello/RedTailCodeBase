import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import timedelta

def read_pricing(df):
    df['Price'] = pd.to_numeric(df['Price'])
    df['Check-in Date'] = pd.to_datetime(df['Check-in Date'])
    df['Report Date'] = pd.to_datetime(df['Report Date'])
    df['Day of Week'] = df['Check-in Date'].dt.day_name()
    df['Check-in Week'] = df['Check-in Date'].dt.to_period('W').apply(lambda r: r.start_time)
    #Get only the most recent data
    return df
def get_and_read_pricing(path):
    df = pd.read_csv(path)
    return read_pricing(df)
def plot_pricing(df, prop, date = "most recent", figsize=(10, 6),save_graph = False,display = True, long_graph = False):
    sns.set_theme(context='notebook', style='whitegrid')
    if date == "most recent":
        date = df['Report Date'].max()
    filtered = df[(df['HWV Property'] == prop) & (df['Report Date'] == date)]

    plt.figure(figsize=figsize)
    g = sns.lineplot(
        x='Check-in Date', 
        y='Price', 
        hue='Competitor',
        data=filtered,
        marker = None if long_graph else 'o', 
        errorbar = None)    
    g.legend(title = "Competitor", loc = 'lower center', ncols = 6, bbox_to_anchor=(0.5, -0.35))
    # Format the x-axis to show dates more sparsely
    if long_graph:
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval = 1))  # Show every 5th day
    else:
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval = 5))  # Show every 5th day
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Rotate date labels for better readability
    plt.gcf().autofmt_xdate()
    plt.title(f"{prop} Compset Pricing Report: {date.strftime('%m/%d/%y')}", fontweight='bold')
    if save_graph:
        plt.savefig(
            os.path.join('Plots', f"{prop}_pricing_{date.strftime('%m-%d-%y')}.png"),
            bbox_inches='tight'
        )
    if display:
        plt.show()
def plot_pricing_facet(df,prop,date="most recent",save_graph = False, display = True, long_graph = False):
    sns.set_theme(context='notebook',style = 'whitegrid')
    
    if date == "most recent":
        date = df['Report Date'].max()
    filtered = df[(df['HWV Property'] == prop) & (df['Report Date'] == date)]
    
    if long_graph:
        g = sns.FacetGrid(filtered,col = 'Competitor',col_wrap = 3, height = 4, aspect = 1.5, sharey = False)
    else:
        g = sns.FacetGrid(filtered,col = 'Competitor',col_wrap = 5, height = 4, aspect = 1.5, sharey = False)
    g.map_dataframe(sns.lineplot, x='Check-in Date',y = 'Price', errorbar = None)
    g.set_titles(col_template='{col_name}',fontweight = 'bold')
    g.set_xlabels('Check in Date')
    
    interval = mdates.MonthLocator(interval=1) if long_graph else mdates.DayLocator(interval=5)
    plt.gca().xaxis.set_major_locator(interval)  # Show every 5th day
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    # Rotate date labels for better readability
    plt.gcf().autofmt_xdate()
    plt.suptitle(f"{prop} Compset Pricing Report: {date.strftime('%m/%d/%y')}",fontweight = 'bold')
    plt.subplots_adjust(top=0.90)
    plt.tight_layout()
    if save_graph:
        plt.savefig(os.path.join('Plots',f"{prop}_pricing_split_{date.strftime('%m-%d-%y')}.png"))
    if display:
        plt.show()
def plot_dow(df,prop,date='most recent',figsize = (10,6),save_graph = False,display = True):
    sns.set_theme(context = 'notebook',style = 'darkgrid')
    if date == "most recent":
        date = df['Report Date'].max()
    
    report_start = df['Check-in Date'].min().strftime('%m/%d/%y')
    report_end = df['Check-in Date'].max().strftime('%m/%d/%y')
    plt.figure(figsize=figsize)
    filtered = df[(df['HWV Property'] == prop) & (df['Report Date'] == date)]
    sns.barplot(data=filtered, x='Day of Week',y='Price',hue='Competitor')
    plt.title(f"{prop} Compset - Average Price by Day of Week: ({report_start} - {report_end})",fontweight = 'bold')
    if save_graph:
        plt.savefig(os.path.join('Plots',f"{prop}_dow_{date.strftime('%m-%d-%y')}.png"))
    if display:
        plt.show()
def plot_room_types(df,prop,date='most recent',save_graph = False, display = True):
    sns.set_theme(context='notebook',style = 'whitegrid')

    if date == "most recent":
        date = df['Report Date'].max()
    
    filtered = df[(df['HWV Property'] == prop) & (df['Report Date'] == date)]
    report_start = df['Check-in Date'].min().strftime('%m/%d/%y')
    report_end = df['Check-in Date'].max().strftime('%m/%d/%y')
    
    comps = filtered['Competitor'].unique()
    num_comps = len(comps)
    fig, ax = plt.subplots(num_comps,1,figsize = (10,4*num_comps))
    for i, comp in enumerate(comps):
        comp_data = filtered[filtered['Competitor'] == comp]
        sns.barplot(data = comp_data, x = 'Price', y = 'Room Type', hue = 'Room Type', ax = ax.flat[i])
        sns.despine(left=True)
        ax.flat[i].set_title(comp)
        ax.flat[i].set_ylabel('')
        if ax.flat[i].get_legend():
            ax.flat[i].get_legend().remove()
    plt.tight_layout()
    
    fig.suptitle(f"{prop} Compset: Average Pricing by Room Type ({report_start} - {report_end})",fontweight = 'bold')
    plt.subplots_adjust(top=0.93)
    
    if save_graph:
        plt.savefig(os.path.join('Plots',f"{prop}_room_types_{date.strftime('%m-%d-%y')}.png"))
    if display:
        plt.show()
def plot_compset_change(df,prop, date = "most recent",save_graph = False,display = True):
    sns.set_theme(context = 'notebook', style = 'whitegrid')

    if date == "most recent":
        date = df['Report Date'].max()
    
    filtered  = df[(df['HWV Property'] == prop) & (df['Report Date'] >= date - timedelta(days = 14))].copy()
    filtered['Formatted Date'] = filtered['Check-in Week'].dt.strftime('%m/%d/%y') + ' - ' + (filtered['Check-in Week'] + timedelta(days = 6)).dt.strftime('%m/%d/%y')
    g = sns.FacetGrid(filtered, col = 'Formatted Date',col_wrap = 2,height = 4, aspect = 1.5, sharey = False)
    g.map_dataframe(sns.lineplot, x = 'Report Date', y = 'Price', hue = 'Competitor', marker = 'o',errorbar = None)


    for ax in g.axes.flat:
        for label in ax.get_xticklabels():
            label.set_rotation(45)

    
    g.set_axis_labels('Report Date','Average Price')
    g.add_legend(title = 'Competitor', loc='lower center',ncols = 5,bbox_to_anchor=(0.5, -0.05))
    g.set_titles(col_template='{col_name}', fontweight = 'bold')
    plt.setp(g.legend.get_title(), fontweight='bold')
    
    plt.suptitle(f"{prop} - Compset Pricing Changes over Time", fontweight = 'bold')
    plt.subplots_adjust(top=0.90)
    plt.tight_layout()
    if save_graph:
        plt.savefig(
            os.path.join('Plots',f"{prop}_compset_change_{date.strftime('%m-%d-%y')}.png"),
            bbox_inches = 'tight')
    
    if display:
        plt.show()
        
def get_graphs(df,prop,date = "most recent", figsize = (10,6),save_graphs = False,plot_changes = False, display = True, long_graph = False):
    plot_pricing(df,prop,date = date,figsize = figsize,save_graph = save_graphs, display = display, long_graph = long_graph)
    plot_pricing_facet(df,prop,date = date,save_graph = save_graphs, display = display, long_graph = long_graph)
    plot_dow(df,prop,date = date,figsize = figsize,save_graph = save_graphs, display = display)
    plot_room_types(df,prop,date = date,save_graph = save_graphs, display = display)
    if plot_changes:
        plot_compset_change(df,prop,date,save_graph = save_graphs, display = display)