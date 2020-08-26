import React from "react";
import {
  Paper,
  Box,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableFooter,
  TableRow,
  TableCell,
  IconButton,
  Typography,
} from "@material-ui/core";
import {
  FirstPage,
  KeyboardArrowLeft,
  KeyboardArrowRight,
  LastPage,
} from "@material-ui/icons";
import { useTable, usePagination, useSortBy } from "react-table";

// see https://github.com/tannerlinsley/react-table/discussions/2296

export const camelCaseToSnakeCase = (str) =>
  str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);

const DataTable = ({
  tableId,
  columns,
  data,
  totalCount,
  fetchData,
  loading,
  pageCount: controlledPageCount,
  pageSize: controlledPageSize,
  sortBy: controlledSortBy,
}) => {
  const {
    rows,
    getTableProps,
    getTableBodyProps,
    headerGroups,
    prepareRow,
    canPreviousPage,
    canNextPage,
    pageCount,
    gotoPage,
    nextPage,
    previousPage,
    state: { pageIndex, pageSize, sortBy },
  } = useTable(
    {
      columns,
      data,
      initialState: {
        pageIndex: 0,
        pageSize: controlledPageSize,
        sortBy: controlledSortBy,
      },
      manualPagination: true,
      manualSortBy: true,
      pageCount: controlledPageCount,
    },

    useSortBy,
    usePagination
  );

  React.useEffect(() => {
    fetchData({ pageIndex, pageSize, sortBy });
  }, [fetchData, pageIndex, pageSize, sortBy]);

  return (
    <Paper>
      <TableContainer>
        <Table {...getTableProps()} id={tableId} size="small">
          <TableHead>
            {headerGroups.map((headerGroup) => (
              <TableRow {...headerGroup.getHeaderGroupProps()}>
                {headerGroup.headers.map((column) => (
                  <TableCell
                    {...column.getHeaderProps(column.getSortByToggleProps())}
                  >
                    {column.render("Header")}
                    <span>
                      {column.isSorted
                        ? column.isSortedDesc
                          ? " 🔽"
                          : " 🔼"
                        : ""}
                    </span>
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableHead>
          <TableBody {...getTableBodyProps()}>
            {rows.map((row, i) => {
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
            })}
          </TableBody>
          <TableFooter>
            <TableRow></TableRow>
          </TableFooter>
        </Table>
      </TableContainer>
      <Box textAlign="right" flexShrink={0} p={1}>
        <Box display="inline" pr={2}>
          <Typography variant="caption">
            {pageIndex * pageSize + 1}-{pageIndex * pageSize + rows.length} of{" "}
            {totalCount}
          </Typography>
        </Box>
        <IconButton
          onClick={() => gotoPage(0)}
          disabled={!canPreviousPage}
          aria-label="first page"
          size="small"
        >
          <FirstPage />
        </IconButton>
        <IconButton
          onClick={previousPage}
          disabled={!canPreviousPage}
          aria-label="previous page"
          size="small"
        >
          <KeyboardArrowLeft />
        </IconButton>
        <IconButton
          onClick={nextPage}
          disabled={!canNextPage}
          aria-label="next page"
          size="small"
        >
          <KeyboardArrowRight />
        </IconButton>
        <IconButton
          onClick={() => gotoPage(pageCount - 1)}
          disabled={!canNextPage}
          aria-label="last page"
          size="small"
        >
          <LastPage />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default DataTable;
