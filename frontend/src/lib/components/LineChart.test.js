import { render } from "@testing-library/svelte";
import { Chart } from "frappe-charts";
import LineChart from "./LineChart.svelte";

const CHART_TITLE = "Progress";

jest.mock("frappe-charts");

it("calls the chart library w/ the correct arguments", () => {
  const datasets = ["data"];
  const height = 42;
  const xLabels = ["XXI", "XXII"];

  render(LineChart, {
    datasets,
    height,
    xLabels,
    title: CHART_TITLE,
  });

  expect(Chart).toHaveBeenCalledTimes(1);
  const chartRootElement = Chart.mock.calls[0][0];
  expect(chartRootElement.tagName).toBe("DIV");
  const chartOptions = Chart.mock.calls[0][1];
  expect(chartOptions).toMatchObject({
    type: "line",
    height,
    title: CHART_TITLE,
    data: {
      datasets,
      labels: xLabels,
    },
  });
});

it("displays a label for the Y axis", () => {
  const yLabel = "mL";

  const { getByText } = render(LineChart, {
    title: CHART_TITLE,
    yLabel,
  });

  const yLabelElement = getByText(yLabel);
  expect(yLabelElement).toBeDefined();
  expect(yLabelElement.getAttribute("aria-hidden")).toBe("true");
});

it("doesn't display a Y-axis container if the label isn't passed", () => {
  const { container } = render(LineChart, {
    title: CHART_TITLE,
  });

  expect(container.getElementsByClassName("y-label")[0]).toBeUndefined();
});
