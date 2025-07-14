/**
 * 知识图谱可视化交互逻辑
 * 负责节点点击展开、关系查询、图谱缩放等交互功能
 */
class KnowledgeGraphVisualizer {
    constructor(chartDomId) {
        // 初始化ECharts实例
        this.chart = echarts.init(document.getElementById(chartDomId));
        this.currentNodes = new Set(); // 记录当前已加载的节点ID
        this.baseOption = this.getDefaultOption();

        // 绑定节点点击事件
        this.chart.on('click', 'series', (params) => {
            if (params.dataType === 'node') {
                this.handleNodeClick(params.data.id);
            }
        });

        // 初始化图谱
        this.chart.setOption(this.baseOption);
    }

    /**
     * 获取默认图表配置
     */
    getDefaultOption() {
        return {
            tooltip: {
                formatter: '{b}' // 显示节点名称
            },
            legend: [{
                data: ['中心人物', '关联人物', '扩展人物'],
                top: 10
            }],
            series: [{
                type: 'graph',
                layout: 'force',
                force: {
                    repulsion: 350,
                    edgeLength: 180,
                    layoutAnimation: true
                },
                roam: true, // 支持缩放和平移
                label: {
                    show: true,
                    position: 'right',
                    fontSize: 14
                },
                edgeLabel: {
                    show: true,
                    formatter: '{c}',
                    fontSize: 12
                },
                data: [],
                links: [],
                categories: [
                    { name: '中心人物', itemStyle: { color: '#43a2f1' } },
                    { name: '关联人物', itemStyle: { color: '#f19443' } },
                    { name: '扩展人物', itemStyle: { color: '#7cb305' } }
                ],
                // 鼠标悬停高亮相关节点和边
                emphasis: {
                    focus: 'adjacency',
                    lineStyle: {
                        width: 5
                    }
                }
            }]
        };
    }

    /**
     * 处理节点点击事件 - 展开子节点
     * @param {string} nodeId 节点ID（人物名称）
     */
    handleNodeClick(nodeId) {
        // 避免重复加载同一节点
        if (this.isNodeExpanded(nodeId)) {
            return;
        }

        // 显示加载动画
        this.showLoading();

        // 调用后端接口查询子节点关系
        $.ajax({
            url: '/relationship',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ "keyword": nodeId }),
            success: (res) => {
                this.hideLoading();
                if (res.status === 200) {
                    this.expandNode(res.respon, nodeId);
                } else {
                    alert(`展开节点失败: ${res.respon}`);
                }
            },
            error: (xhr) => {
                this.hideLoading();
                alert(`请求失败: ${xhr.statusText}`);
            }
        });
    }

    /**
     * 展开节点 - 添加新的关联节点和关系
     * @param {Object} data 后端返回的关系数据
     * @param {string} centerNodeId 中心节点ID
     */
    expandNode(data, centerNodeId) {
        const currentOption = this.chart.getOption();
        const newNodes = [];
        const newLinks = [];

        // 标记中心节点为已展开
        this.markNodeAsExpanded(centerNodeId);

        // 处理新节点和关系
        data.nodes.forEach(node => {
            if (!this.currentNodes.has(node.id)) {
                // 为新节点设置分类（扩展人物）
                node.category = 2;
                newNodes.push(node);
                this.currentNodes.add(node.id);
            }
        });

        data.lines.forEach(link => {
            newLinks.push({
                source: link.from,
                target: link.to,
                label: { text: link.text }
            });
        });

        // 合并新数据并刷新图表
        currentOption.series[0].data = [...currentOption.series[0].data,...newNodes];
        currentOption.series[0].links = [...currentOption.series[0].links,...newLinks];
        this.chart.setOption(currentOption);
    }

    /**
     * 初始加载图谱数据
     * @param {Object} initialData 初始关系数据
     */
    loadInitialData(initialData) {
        this.currentNodes.clear();
        // 记录初始节点
        initialData.nodes.forEach(node => {
            this.currentNodes.add(node.id);
        });
        // 设置初始数据
        this.baseOption.series[0].data = initialData.nodes;
        this.baseOption.series[0].links = initialData.lines;
        this.chart.setOption(this.baseOption);
    }

    /**
     * 检查节点是否已展开
     * @param {string} nodeId 节点ID
     */
    isNodeExpanded(nodeId) {
        // 在节点数据中查找是否有展开标记
        const nodeData = this.chart.getOption().series[0].data.find(n => n.id === nodeId);
        return nodeData && nodeData.expanded;
    }

    /**
     * 标记节点为已展开
     * @param {string} nodeId 节点ID
     */
    markNodeAsExpanded(nodeId) {
        const option = this.chart.getOption();
        const nodeIndex = option.series[0].data.findIndex(n => n.id === nodeId);
        if (nodeIndex!== -1) {
            option.series[0].data[nodeIndex].expanded = true;
            // 高亮已展开节点（增大尺寸）
            option.series[0].data[nodeIndex].symbolSize = 65;
            this.chart.setOption(option);
        }
    }

    /**
     * 显示加载动画
     */
    showLoading() {
        this.chart.showLoading({
            text: '加载中...',
            fontSize: 16,
            maskColor: 'rgba(255, 255, 255, 0.7)'
        });
    }

    /**
     * 隐藏加载动画
     */
    hideLoading() {
        this.chart.hideLoading();
    }

    /**
     * 重置图谱
     */
    resetGraph() {
        this.currentNodes.clear();
        this.chart.setOption(this.getDefaultOption());
    }
}

// 页面加载完成后初始化可视化器
$(function() {
    // 初始化图谱可视化器
    const graphVisualizer = new KnowledgeGraphVisualizer('graph');

    // 替换search.html中的渲染函数
    window.renderGraph = function(data) {
        graphVisualizer.loadInitialData(data);
    };

    // 为查询按钮绑定重置功能
    $('#resetGraph').click(function() {
        graphVisualizer.resetGraph();
    });
});
