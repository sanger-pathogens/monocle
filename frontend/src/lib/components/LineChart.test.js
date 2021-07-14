import { render } from "@testing-library/svelte";
import { Chart } from "frappe-charts";
import LineChart from "./LineChart.svelte";

jest.mock("frappe-charts");

it("calls the chart library w/ the correct arguments", () => {
  const datasets = ["data"];
  const height = 42;
  const labels = ["XXI", "XXII"];
  const title = "Chart Title";

  const { getByText } = render(LineChart, {
    datasets,
    height,
    labels,
    title
  });

  expect(Chart).toHaveBeenCalledTimes(1);
  const chartRootElement = Chart.mock.calls[0][0];
  expect(chartRootElement.tagName).toBe("DIV");
  const chartOptions = Chart.mock.calls[0][1];
  expect(chartOptions).toMatchObject({
    type: "line",
    height,
    title,
    data: {
      datasets,
      labels,
    }
  });
});
