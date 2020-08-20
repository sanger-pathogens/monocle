import React from "react";
import { render, fireEvent } from "@testing-library/react";

import DataTable from "./DataTable";

test("can visit next page", async () => {
  const columns = [
    {
      Header: "Numeric Field",
      accessor: "numericField",
    },
  ];
  const totalCount = 40;
  const pageSize = 10;
  const pageCount = 4;
  const allData = new Array(totalCount).fill({ numericField: 0 });
  let data = allData.slice(0, 10);
  const fetchData = jest.fn().mockImplementation(({ pageSize, pageIndex }) => {
    data = allData.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize);
  });
  const { container, getByLabelText, getByText } = render(
    <DataTable
      tableId="testTable"
      columns={columns}
      data={data}
      totalCount={totalCount}
      fetchData={fetchData}
      pageCount={pageCount}
      pageSize={pageSize}
    />
  );

  expect(getByLabelText("next page")).toBeInTheDocument();
  expect(getByText("1-10 of 40")).toBeInTheDocument();

  fireEvent.click(getByLabelText("next page"));

  expect(getByText("11-20 of 40")).toBeInTheDocument();
});
