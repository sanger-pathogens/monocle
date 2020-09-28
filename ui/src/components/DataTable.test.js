import React from "react";
import { render, fireEvent } from "@testing-library/react";

import DataTable from "./DataTable";

describe("DataTable.pagination", () => {
  const columns = [
    {
      Header: "Numeric Field",
      accessor: "numericField",
    },
    {
      Header: "Other Numeric Field",
      accessor: "otherNumericField",
    },
    {
      Header: "String Field",
      accessor: "stringField",
    },
  ];
  const totalCount = 40;
  const pageSize = 10;
  const pageCount = 4;
  const sortBy = [{ id: "numericField", desc: false }];
  const allData = new Array(totalCount).fill(0).map((_, i) => ({
    numericField: i,
    otherNumericField: (i % 3) * totalCount + i,
    stringField: String.fromCharCode(65 + i),
  }));

  let data;
  let fetchData;
  beforeEach(() => {
    data = allData.slice(0, 10);
    fetchData = jest
      .fn()
      .mockImplementation(({ pageSize, pageIndex, sortBy }) => {
        const comparator = (a, b) => {
          const vA = a[sortBy.id];
          const vB = b[sortBy.id];
          const value = sortBy.desc ? -1 : 1;
          if (vA < vB) {
            return -1 * value;
          } else if (vA > vB) {
            return value;
          } else {
            return 0;
          }
        };
        data = allData
          .sort(comparator)
          .slice(pageIndex * pageSize, (pageIndex + 1) * pageSize);
      });
  });

  describe("DataTable.sorting", () => {
    it("has default sorting applied", async () => {
      render(
        <DataTable
          tableId="testTable"
          columns={columns}
          data={data}
          totalCount={totalCount}
          fetchData={fetchData}
          pageCount={pageCount}
          pageSize={pageSize}
          sortBy={sortBy}
        />
      );

      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 0,
        sortBy: [{ desc: false, id: "numericField" }],
      });
    });

    it("has default sorting reversed when default sort column clicked", async () => {
      const { getByText } = render(
        <DataTable
          tableId="testTable"
          columns={columns}
          data={data}
          totalCount={totalCount}
          fetchData={fetchData}
          pageCount={pageCount}
          pageSize={pageSize}
          sortBy={sortBy}
        />
      );

      fireEvent.click(getByText("Numeric Field"));

      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 0,
        sortBy: [{ desc: true, id: "numericField" }],
      });
    });
  });

  describe("DataTable.pagination", () => {
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
          sortBy={[]}
        />
      );

      expect(getByLabelText("next page")).toBeInTheDocument();
      expect(getByText("1-10 of 40")).toBeInTheDocument();
      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 0,
        sortBy: [],
      });

      fireEvent.click(getByLabelText("next page"));

      expect(getByText("11-20 of 40")).toBeInTheDocument();
      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 1,
        sortBy: [],
      });
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
          sortBy={[]}
        />
      );

      expect(getByLabelText("last page")).toBeInTheDocument();
      expect(getByText("1-10 of 40")).toBeInTheDocument();
      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 0,
        sortBy: [],
      });

      fireEvent.click(getByLabelText("last page"));

      expect(getByText("31-40 of 40")).toBeInTheDocument();
      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 3,
        sortBy: [],
      });
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
          sortBy={[]}
        />
      );

      expect(getByLabelText("next page")).toBeInTheDocument();
      expect(getByText("1-10 of 40")).toBeInTheDocument();
      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 0,
        sortBy: [],
      });

      fireEvent.click(getByLabelText("next page"));

      expect(getByText("11-20 of 40")).toBeInTheDocument();
      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 1,
        sortBy: [],
      });

      fireEvent.click(getByLabelText("previous page"));

      expect(getByText("1-10 of 40")).toBeInTheDocument();
      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 0,
        sortBy: [],
      });
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
          sortBy={[]}
        />
      );

      expect(getByLabelText("last page")).toBeInTheDocument();
      expect(getByText("1-10 of 40")).toBeInTheDocument();
      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 0,
        sortBy: [],
      });

      fireEvent.click(getByLabelText("last page"));

      expect(getByText("31-40 of 40")).toBeInTheDocument();
      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 3,
        sortBy: [],
      });

      fireEvent.click(getByLabelText("first page"));

      expect(getByText("1-10 of 40")).toBeInTheDocument();
      expect(fetchData).toHaveBeenCalledWith({
        pageSize: 10,
        pageIndex: 0,
        sortBy: [],
      });
    });
  });
});
