window.onload = function () {
    // 原标签云初始化逻辑（保留）
    const radius = 120;
    const dtr = Math.PI / 180;
    const mcList = [];
    const aTags = document.querySelectorAll("#tagsList a");
    
    aTags.forEach(tag => {
        mcList.push({ width: tag.offsetWidth, height: tag.offsetHeight });
        tag.addEventListener("click", function (e) {
            e.preventDefault();
            const charName = this.textContent;
            // 调用关系查询接口
            fetch(`/search_name?name=${charName}`)
                .then(res => res.json())
                .then(data => renderGraph(data));
        });
    });

    // 关系图渲染函数
    function renderGraph(graphData) {
        const graphDom = document.createElement("div");
        graphDom.id = "temp-graph";
        graphDom.style.width = "800px";
        graphDom.style.height = "600px";
        graphDom.style.position = "fixed";
        graphDom.style.top = "100px";
        graphDom.style.left = "50%";
        graphDom.style.transform = "translateX(-50%)";
        graphDom.style.zIndex = 999;
        document.body.appendChild(graphDom);

        const myChart = echarts.init(graphDom);
        const option = {
            series: [{
                type: "graph",
                layout: "force",
                nodes: graphData.nodes.map(name => ({ name })),
                links: graphData.links.map(link => ({
                    source: link.source,
                    target: link.target,
                    label: { show: true, formatter: link.label }
                })),
                force: { repulsion: 1200 }
            }]
        };
        myChart.setOption(option);

        // 点击空白处关闭
        graphDom.addEventListener("click", (e) => {
            if (e.target === graphDom) {
                graphDom.remove();
            }
        });
    }

    // 原标签云动画逻辑（保留）
    function update() { /* ... */ }
    setInterval(update, 30);
};
