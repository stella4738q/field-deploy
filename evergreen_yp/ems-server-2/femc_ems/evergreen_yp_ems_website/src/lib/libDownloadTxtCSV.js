export default function(content, filename) {
    content = content.replace(/#/g, '');
    var uri = 'data:text/csv;charset=utf-8,%EF%BB%BF' + content;
    var downloadLink = document.createElement("a");
    downloadLink.href = uri;
    downloadLink.download = filename+".csv";

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
}