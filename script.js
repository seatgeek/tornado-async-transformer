// globals ace

const editorSource = ace.edit("editor-source");
editorSource.setTheme("ace/theme/tomorrow_night");
editorSource.session.setMode("ace/mode/python");

const editorTransformed = ace.edit("editor-transformed");
editorTransformed.setReadOnly(true);
editorTransformed.setTheme("ace/theme/tomorrow_night");
editorTransformed.session.setMode("ace/mode/python");

async function fetchTransformedSource(source) {
  const response = await fetch("/api/transform", {
    method: "POST",
    body: JSON.stringify({ source })
  });
  const body = await response.json();
  return body.source;
}

let calls = 0;
async function onEditorUpdated() {
  const call = ++calls;
  const transformed = await fetchTransformedSource(editorSource.getValue());
  if (call === calls) {
    editorTransformed.setValue(transformed);
    editorSource.clearSelection();
    editorTransformed.clearSelection();
  }
}

editorSource.setValue(`"""
A simple coroutine.
"""
from tornado import gen
@gen.coroutine
def call_api():
    response = yield fetch()
    if response.status != 200:
        raise BadStatusError()
    raise gen.Return(response.data)
`);
onEditorUpdated();
editorSource.on("change", onEditorUpdated);
