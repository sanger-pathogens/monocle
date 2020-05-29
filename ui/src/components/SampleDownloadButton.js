import React from "react";

const downloadData = () => {
                fetch('http://127.0.0.1:8000/data')
                        .then(response => {
                                response.blob().then(blob => {
                                        let url = window.URL.createObjectURL(blob);
                                        let a = document.createElement('a');
                                        a.href = url;
                                        a.download = 'test.csv';
                                        a.click();
                                });
                                //window.location.href = response.url;
                });
        }

export default downloadData;
