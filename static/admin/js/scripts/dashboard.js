$(document).ready(function() {

    // Chart in Dashboard version 1
    let echartElemPie = document.getElementById('echartPie');
    if (echartElemPie) {
        let echartPie = echarts.init(echartElemPie);
        echartPie.setOption({
            color: ['#62549c', '#7566b5', '#7d6cbb', '#8877bd', '#9181bd', '#6957af'],
            tooltip: {
                show: true,
                backgroundColor: 'rgba(0, 0, 0, .8)'
            },

            series: [{
                name: 'Månedtlig bruk av forskjellige ',
                type: 'pie',
                radius: '60%',
                center: ['50%', '50%'],
                data: [
                    { value: 1000, name: '3rd year' },
                    { value: 310, name: '2nd year' },
                    { value: 234, name: '1st year' }
                ],
                itemStyle: {
                    emphasis: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }]
        });
        $(window).on('resize', function() {
            setTimeout(() => {
                echartPie.resize();
            }, 500);
        });
    }

    // Chart in Dashboard version 1
    let echartElem1 = document.getElementById('echart1');
    if (echartElem1) {
        let echart1 = echarts.init(echartElem1);
        echart1.setOption({
            ...echartOptions.lineFullWidth,
            ... {
                series: [{
                    data: [30, 40, 20, 50, 40, 80, 90],
                    ...echartOptions.smoothLine,
                    markArea: {
                        label: {
                            show: true
                        }
                    },
                    areaStyle: {
                        color: 'rgba(102, 51, 153, .2)',
                        origin: 'start'
                    },
                    lineStyle: {
                        color: '#663399',
                    },
                    itemStyle: {
                        color: '#663399'
                    }
                }]
            }
        });
        $(window).on('resize', function() {
            setTimeout(() => {
                echart1.resize();
            }, 500);
        });
    }
    // Chart in Dashboard version 1
    let echartElem2 = document.getElementById('echart2');
    if (echartElem2) {
        let echart2 = echarts.init(echartElem2);
        echart2.setOption({
            ...echartOptions.lineFullWidth,
            ... {
                series: [{
                    data: [30, 10, 40, 10, 40, 20, 90],
                    ...echartOptions.smoothLine,
                    markArea: {
                        label: {
                            show: true
                        }
                    },
                    areaStyle: {
                        color: 'rgba(255, 193, 7, 0.2)',
                        origin: 'start'
                    },
                    lineStyle: {
                        color: '#FFC107'
                    },
                    itemStyle: {
                        color: '#FFC107'
                    }
                }]
            }
        });
        $(window).on('resize', function() {
            setTimeout(() => {
                echart2.resize();
            }, 500);
        });
    }
    // Chart in Dashboard version 1
    let echartElem3 = document.getElementById('echart3');
    if (echartElem3) {
        let echart3 = echarts.init(echartElem3);
        echart3.setOption({
            ...echartOptions.lineNoAxis,
            ... {
                series: [{
                    data: [5, 8, 2, 10, 0, 8, 6, 10, 4, 5, 0, 0, 5, 4, 3, 7, 6, 4, 2, 1, 10, 12, 5, 15, 1, 2, 1, 1,4],
                    lineStyle: {
                        color: 'rgba(102, 51, 153, 0.8)',
                        width: 3,
                        ...echartOptions.lineShadow
                    },
                    label: { show: true, color: '#212121' },
                    type: 'line',
                    smooth: true,
                    itemStyle: {
                        borderColor: 'rgba(102, 51, 153, 1)'
                    }
                }]
            }
        });
        $(window).on('resize', function() {
            setTimeout(() => {
                echart3.resize();
            }, 500);
        });
    }

});