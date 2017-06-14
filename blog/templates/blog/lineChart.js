
/**
 * Created by ws on 4/26/17.
 */
function loadLineChart(elementId, dataset) {
	var svg = d3.select("#" + elementId);
	var strs = svg.attr("viewBox").split(" ");
	alert(dataset);
	var width = strs[2];
	var height = strs[3];

	//��߿�
	var padding = {
		top : 50,
		right : 50,
		bottom : 50,
		left : 50
	};

	var names = new Array();
	//����GDP�����ֵ
	var gdpmax = 0;
	for (var i = 0; i < dataset.length; i++) {
		var currGdp = d3.max(dataset[i].gdp, function (d) {
				return d[1];
			});
		if (currGdp > gdpmax)
			gdpmax = currGdp;

	}
	var gdpnumb = dataset[0].gdp.length;
	for (var j = 0; j < gdpnumb; j++) {
		names[j] = (dataset[0].gdp[j])[0];
	}

	alert(names);
	var xScale = d3.scale.linear()
		.domain([2000, 2013])
		.range([0, width - padding.left - padding.right]);
	//	var xScale = d3.scale.ordinal()
	//	.domain(names)
	//	.rangeRoundBands([0, width - padding.left - padding.right]);

	var yScale = d3.scale.linear()
		.domain([0, gdpmax * 1.1])
		.range([height - padding.top - padding.bottom, 0]);

	//����һ��ֱ��������
	var linePath = d3.svg.line()
		.x(function (d) {
			return xScale(d[0]);
		})
		.y(function (d) {
			return yScale(d[1]);
		})
		.interpolate("basis");

	//����������ɫ
	var colors = [d3.rgb(0, 0, 255), d3.rgb(0, 255, 0)];

	//���·��
	svg.selectAll("path") //ѡ��<svg>�����е�<path>
	.data(dataset) //������
	.enter() //ѡ��enter����
	.append("path") //����㹻������<path>Ԫ��
	.attr("transform", "translate(" + padding.left + "," + padding.top + ")")
	.attr("d", function (d) {
		return linePath(d.gdp); //����ֱ���������õ���·��
	})
	.attr("fill", "none")
	.attr("stroke-width", 3)
	.attr("stroke", function (d, i) {
		return colors[i];
	});

	//��Ӵ�ֱ��x��Ķ�����
	var vLine = svg.append("line")
		.attr("class", "focusLine")
		.style("display", "none");

	//���һ����ʾ��
	var tooltip = d3.select("body")
		.append("div")
		.attr("class", "tooltip")
		.style("opacity", 0.0);

	var title = tooltip.append("div")
		.attr("class", "title");

	var des = tooltip.selectAll(".des")
		.data(dataset)
		.enter()
		.append("div");

	var desColor = des.append("div")
		.attr("class", "desColor");

	var desText = des.append("div")
		.attr("class", "desText");

	//���һ��͸���ļ�������¼��õľ���
	svg.append("rect")
	.attr("class", "overlay")
	.attr("x", padding.left)
	.attr("y", padding.top)
	.attr("width", width - padding.left - padding.right)
	.attr("height", height - padding.top - padding.bottom)
	.on("mouseover", function () {
		tooltip.style("left", (d3.event.pageX) + "px")
		.style("top", (d3.event.pageY + 20) + "px")
		.style("opacity", 1.0);

		vLine.style("display", null);
	})
	.on("mouseout", function () {
		tooltip.style("opacity", 0.0);
		vLine.style("display", "none");
	})
	.on("mousemove", mousemove);

	function mousemove() {
		/* �������͸�������ڻ���ʱ���� */

		//���ߵ�Դ����
		var data = dataset[0].gdp;

		//��ȡ��������͸���������Ͻǵ����꣬���Ͻ�����Ϊ(0,0)
		var mouseX = d3.mouse(this)[0] - padding.left;
		var mouseY = d3.mouse(this)[1] - padding.top;

		//ͨ�������ߵķ���������ԭ�����е�ֵ������x0Ϊĳ����ݣ�y0ΪGDPֵ
		var x0 = xScale.invert(mouseX);
		var y0 = yScale.invert(mouseY);

		//��x0�������룬���x0��2005.6���򷵻�2006�������2005.2���򷵻�2005
		x0 = Math.round(x0);

		//������ԭ������x0��ֵ��������������
		var bisect = d3.bisector(function (d) {
				return d[0];
			}).left;
		var index = bisect(data, x0);

		//��ȡ��ݺ�gdp����
		var year = x0;
		var gdp = [];

		for (var k = 0; k < dataset.length; k++) {
			gdp[k] = {
				country : dataset[k].country,
				value : dataset[k].gdp[index][1]
			};
		}

		//������ʾ��ı������֣���ݣ�
		title.html("<strong>" + year + "��</strong>");

		//������ɫ��ǵ���ɫ
		desColor.style("background-color", function (d, i) {
			return colors[i];
		});

		//�����������ֵ�����
		desText.html(function (d, i) {
			return gdp[i].country + "\t" + "<strong>" + gdp[i].value + "</strong>";
		});

		//������ʾ���λ��
		tooltip.style("left", (d3.event.pageX) + "px")
		.style("top", (d3.event.pageY + 20) + "px");

		//��ȡ��ֱ�����ߵ�x����
		var vlx = xScale(data[index][0]) + padding.left;

		//�趨��ֱ�����ߵ������յ�
		vLine.attr("x1", vlx)
		.attr("y1", padding.top)
		.attr("x2", vlx)
		.attr("y2", height - padding.bottom);
	}

	var markStep = 80;

	var gMark = svg.selectAll(".gMark")
		.data(dataset)
		.enter()
		.append("g")
		.attr("transform", function (d, i) {
			return "translate(" + (padding.left + i * markStep) + "," + (height - padding.bottom + 40) + ")";
		});

	gMark.append("rect")
	.attr("x", 0)
	.attr("y", 0)
	.attr("width", 10)
	.attr("height", 10)
	.attr("fill", function (d, i) {
		return colors[i];
	});

	gMark.append("text")
	.attr("dx", 15)
	.attr("dy", ".5em")
	.attr("fill", "black")
	.text(function (d) {
		return d.country;
	});

	//x��
	var xAxis = d3.svg.axis()
		.scale(xScale)
		.ticks(5)
		.tickFormat(d3.format("d"))
		.orient("bottom");

	//y��
	var yAxis = d3.svg.axis()
		.scale(yScale)
		.orient("left");

	svg.append("g")
	.attr("class", "axis")
	.attr("transform", "translate(" + padding.left + "," + (height - padding.bottom) + ")")
	.call(xAxis);

	svg.append("g")
	.attr("class", "y axis")
	.attr("transform", "translate(" + padding.left + "," + padding.top + ")")
	.call(yAxis);

	function updateLineChart() {

		this.update = function (updateData) {
			//xScale.domain(updateData,function(d){return d.name});
			var numValues = updateData.length;
			var updategdpmax = 0;
			for (var i = 0; i < updateData.length; i++) {
				var currGdp = d3.max(updateData[i].gdp, function (d) {
						return d[1];
					});
				if (currGdp > updategdpmax)
					updategdpmax = currGdp;
			}

			yScale = d3.scale.linear()
				.domain([0, updategdpmax * 1.1])
				.range([height - padding.top - padding.bottom, 0]);
			yAxis = d3.svg.axis()
				.scale(yScale)
				.orient("left");
			svg.selectAll("g.y.axis")
			.call(yAxis);

			svg.selectAll("path") //ѡ��<svg>�����е�<path>
			.data(updateData) //������
			.transition()
			.duration(2000)
			.ease("linear")
			.attr("d", function (d) {

				return linePath(d.gdp); //����ֱ���������õ���·��
			});

		}

	}
	return new updateLineChart();
}
