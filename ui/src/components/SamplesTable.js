import React from "react";
import { useLazyQuery } from "@apollo/react-hooks";
import gql from "graphql-tag";
import {
  Paper,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  LinearProgress,
} from "@material-ui/core";
import { useTable, usePagination } from "react-table";

import { useDownloading } from "../downloading";
import SampleDownloadButton from "./SampleDownloadButton";

export const SAMPLES_LIST_QUERY = gql`
  query SamplesList($offset: Int) {
    samplesList {
      results(limit: 5, offset: $offset) {
        laneId
        sampleId
        publicName
        hostStatus
        serotype
        submittingInstitution {
          name
          country # TODO: replace submittingInstitution.country with samples.country
        }
      }
      totalCount
    }
  }
`;

// see https://github.com/tannerlinsley/react-table/discussions/2296
function OrderTable({
  columns,
  data,
  fetchData,
  loading,
  pageCount: controlledPageCount,
}) {
  console.log(controlledPageCount);
  const {
    rows,
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    page,
    canPreviousPage,
    canNextPage,
    pageOptions,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    setPageSize,
    state: { pageIndex, pageSize },
  } = useTable(
    {
      columns,
      data,
      initialState: { pageIndex: 0 }, // Pass our hoisted table state
      manualPagination: true, // Tell the usePagination
      pageCount: controlledPageCount,
    },
    usePagination
  );

  React.useEffect(() => {
    fetchData({ pageIndex, pageSize });
  }, [fetchData, pageIndex, pageSize]);

  // Render the UI for your table
  return (
    <TableContainer component={Paper}>
      <Table {...getTableProps()} size="small">
        <TableHead>
          {headerGroups.map((headerGroup) => (
            <TableRow {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map((column) => (
                <TableCell {...column.getHeaderProps()}>
                  {column.render("Header")}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableHead>
        <TableBody {...getTableBodyProps()}>
          {rows
            ? rows.map((row, i) => {
                prepareRow(row);
                return (
                  <TableRow {...row.getRowProps()}>
                    {row.cells.map((cell) => {
                      return (
                        <TableCell {...cell.getCellProps()}>
                          {cell.render("Cell")}
                        </TableCell>
                      );
                    })}
                  </TableRow>
                );
              })
            : null}
        </TableBody>
      </Table>
    </TableContainer>
  );
}

const Samples = () => {
  const columns = React.useMemo(
    () => [
      {
        Header: "Metadata",
        columns: [
          {
            Header: "Lane ID",
            accessor: "laneId",
            // canSort: true
          },
        ],
      },
    ],
    []
  );

  //   https://github.com/tannerlinsley/react-table/discussions/2296
  let [loadData, { loading, error, data }] = useLazyQuery(SAMPLES_LIST_QUERY);

  const fetchIdRef = React.useRef(0);

  const fetchData = React.useCallback(({ pageSize, pageIndex }) => {
    // sortBy
    const fetchId = ++fetchIdRef.current;
    if (fetchId === fetchIdRef.current) {
      const offset = pageSize * pageIndex;
      loadData({
        variables: {
          offset,
        },
      });
    }
  }, []);

  const pageSize = 5;
  const pageCount = data
    ? Math.ceil(data.samplesList.totalCount / pageSize)
    : 0;
  const allData = data ? data.samplesList.results : [];

  return (
    <OrderTable
      columns={columns}
      data={allData}
      fetchData={fetchData}
      loading={loading}
      pageCount={pageCount}
    />
  );
};

export default Samples;
