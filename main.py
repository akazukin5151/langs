import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

with open('./out.json', 'r') as f:
    j = json.load(f)

repos = j['data']['user']['repositories']['nodes']
x = [
    (repo['createdAt'], lang['node']['name'], lang['node']['color'], lang['size'])
    for repo in repos
    for lang in repo['languages']['edges']
]

df = pd.DataFrame(x, columns=['createdAt', 'name', 'color', 'size'])
#df['createdAt'] = pd.to_datetime(df.createdAt)

# total size of the codebase for each repo
df = df.merge(
    df.groupby('createdAt')['size'].sum().reset_index(), on='createdAt',
    suffixes=(None, '_total')
)

df['size_pct'] = df['size'] / df['size_total']

_, ax = plt.subplots(figsize=(20, 9))

ax.xaxis.set_major_formatter(FuncFormatter(lambda _, pos: str(pos)))

for i in df['createdAt'].unique():
    sub = df[df['createdAt'] == i]
    names = sub.name.unique()
    for idx, name in enumerate(names):
        here = sub[sub.name == name]

        bottom = None
        if idx != 0:
            # Need to calculate the cumulative sum
            bottom = sub[sub.name.isin(sub.name.iloc[:idx])].size_pct.sum()

        ax.bar(
            x=here['createdAt'],
            height=here['size_pct'],
            color=here.color.iloc[0],
            bottom=bottom
        )


freq = df.name.value_counts().reset_index()
freq.rename(columns={'name': 'freq', 'index': 'name'}, inplace=True)
df = df.merge(freq, on='name')

labels = (
    df.sort_values('freq', ascending=False)[['name', 'color']]
      .drop_duplicates(subset='name')
)

legend_elements = [
    Line2D(
        [0], [0], marker='o', color='w', label=row['name'],
        markerfacecolor=row['color'], markersize=10
    )
    for _, row in labels.iterrows()
]

ax.legend(
    handles=legend_elements,
    ncol=len(df.name.unique()),
    loc='upper center',
    bbox_to_anchor=(0.5, 1.01)
)

plt.xlabel('Repository creation order')
plt.ylabel('% of size of codebase')
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
plt.tight_layout()
plt.savefig('out.png')
