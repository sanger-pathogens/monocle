import React from 'react';

class DownloadFile extends React.Component {
	
	constructor(props) {
		super(props);
	}
	
	downloadEmployeeData = () => {
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
	
	render() {
		return (
			<div id="container">
			<button onClick={this.downloadEmployeeData}>Download</button>
			</div>
		)
	}

}

export default DownloadFile;
