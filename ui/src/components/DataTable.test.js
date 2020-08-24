import React from "react";
import { render, fireEvent } from "@testing-library/react";

import DataTable from "./DataTable";

describe("DataTable.pagination", () => {
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

  let data;
  let fetchData;
  beforeEach(() => {
    data = allData.slice(0, 10);
    fetchData = jest.fn().mockImplementation(({ pageSize, pageIndex }) => {
      data = allData.slice(pageIndex * pageSize, (pageIndex + 1) * pageSize);
    });
  });

  it("can visit next page", async () => {
    const { getByLabelText, getByText } = render(
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
    expect(fetchData).toHaveBeenCalledWith({ pageSize: 10, pageIndex: 0 });

    fireEvent.click(getByLabelText("next page"));

    expect(getByText("11-20 of 40")).toBeInTheDocument();
    expect(fetchData).toHaveBeenCalledWith({ pageSize: 10, pageIndex: 1 });
  });

  it("can visit last page", async () => {
    const { getByLabelText, getByText } = render(
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

    expect(getByLabelText("last page")).toBeInTheDocument();
    expect(getByText("1-10 of 40")).toBeInTheDocument();
    expect(fetchData).toHaveBeenCalledWith({ pageSize: 10, pageIndex: 0 });

    fireEvent.click(getByLabelText("last page"));

    expect(getByText("31-40 of 40")).toBeInTheDocument();
    expect(fetchData).toHaveBeenCalledWith({ pageSize: 10, pageIndex: 3 });
  });

  it("can visit previous page", async () => {
    const { getByLabelText, getByText } = render(
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
    expect(fetchData).toHaveBeenCalledWith({ pageSize: 10, pageIndex: 0 });

    fireEvent.click(getByLabelText("next page"));

    expect(getByText("11-20 of 40")).toBeInTheDocument();
    expect(fetchData).toHaveBeenCalledWith({ pageSize: 10, pageIndex: 1 });

    fireEvent.click(getByLabelText("previous page"));

    expect(getByText("1-10 of 40")).toBeInTheDocument();
    expect(fetchData).toHaveBeenCalledWith({ pageSize: 10, pageIndex: 0 });
  });

  it("can visit first page", async () => {
    const { getByLabelText, getByText } = render(
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

    expect(getByLabelText("last page")).toBeInTheDocument();
    expect(getByText("1-10 of 40")).toBeInTheDocument();
    expect(fetchData).toHaveBeenCalledWith({ pageSize: 10, pageIndex: 0 });

    fireEvent.click(getByLabelText("last page"));

    expect(getByText("31-40 of 40")).toBeInTheDocument();
    expect(fetchData).toHaveBeenCalledWith({ pageSize: 10, pageIndex: 3 });

    fireEvent.click(getByLabelText("first page"));

    expect(getByText("1-10 of 40")).toBeInTheDocument();
    expect(fetchData).toHaveBeenCalledWith({ pageSize: 10, pageIndex: 0 });
  });
});
