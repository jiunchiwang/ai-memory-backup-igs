/**
 * compile-proto.js — 從 .proto 產出 Cocos 3.6.2 可用的 CJS static module
 * 不依賴 protobufjs-cli（Node 25 有 reservedRe bug），純用 runtime API
 * 
 * Usage: node compile-proto.js <input.proto> <output.js>
 */
const fs = require('fs');
const path = require('path');

const protoFile = process.argv[2] || path.join(__dirname, 'ar2pq9Proto.proto');
const outputJs = process.argv[3] || path.join(path.dirname(protoFile), path.basename(protoFile, '.proto') + '.js');

// Use protobufjs from the project's node_modules
const pbPath = require.resolve('protobufjs', { paths: [path.join(path.dirname(protoFile), 'node_modules'), path.dirname(protoFile)] });
const protobuf = require(pbPath);

// Load the .proto file
const root = protobuf.loadSync(protoFile);
const ns = root.nestedArray[0]; // First package
const namespace = ns.name;

console.log(`Compiling ${protoFile} (package: ${namespace})`);

// Generate CJS static module manually
let output = `/*eslint-disable block-scoped-var, id-length, no-control-regex, no-magic-numbers, no-prototype-builtins, no-redeclare, no-shadow, no-var, sort-vars*/
"use strict";

var $protobuf = require("protobufjs/minimal");

var $Reader = $protobuf.Reader, $Writer = $protobuf.Writer, $util = $protobuf.util;

var $root = $protobuf.roots["default"] || ($protobuf.roots["default"] = {});

$root.${namespace} = (function() {
    var ${namespace} = {};
`;

// Generate each message type
function generateMessage(msg, indent) {
  const name = msg.name;
  const fields = msg.fieldsArray || [];
  
  let code = '';
  code += `${indent}${namespace}.${name} = (function() {\n`;
  code += `${indent}    function ${name}(properties) {\n`;
  
  // Initialize repeated fields
  const repeatedFields = fields.filter(f => f.repeated);
  for (const f of repeatedFields) {
    code += `${indent}        this.${f.name} = [];\n`;
  }
  
  code += `${indent}        if (properties)\n`;
  code += `${indent}            for (var keys = Object.keys(properties), i = 0; i < keys.length; ++i)\n`;
  code += `${indent}                if (properties[keys[i]] != null)\n`;
  code += `${indent}                    this[keys[i]] = properties[keys[i]];\n`;
  code += `${indent}    }\n\n`;
  
  // Prototype defaults
  for (const f of fields) {
    if (f.repeated) {
      code += `${indent}    ${name}.prototype.${f.name} = $util.emptyArray;\n`;
    } else if (f.type === 'string') {
      code += `${indent}    ${name}.prototype.${f.name} = "";\n`;
    } else if (f.type === 'bool') {
      code += `${indent}    ${name}.prototype.${f.name} = false;\n`;
    } else if (f.type === 'double' || f.type === 'float') {
      code += `${indent}    ${name}.prototype.${f.name} = 0;\n`;
    } else if (f.type === 'int32' || f.type === 'int64' || f.type === 'uint32') {
      code += `${indent}    ${name}.prototype.${f.name} = 0;\n`;
    } else if (f.resolvedType) {
      code += `${indent}    ${name}.prototype.${f.name} = null;\n`;
    } else {
      code += `${indent}    ${name}.prototype.${f.name} = 0;\n`;
    }
  }
  
  code += `\n${indent}    ${name}.create = function create(properties) {\n`;
  code += `${indent}        return new ${name}(properties);\n`;
  code += `${indent}    };\n\n`;
  
  // decode (simple: just return the object as-is since we use JSON transport in mock)
  code += `${indent}    ${name}.decode = function decode(reader, length) {\n`;
  code += `${indent}        if (reader instanceof $Reader) {\n`;
  code += `${indent}            // Binary decode - not needed for mock, return empty\n`;
  code += `${indent}            return new ${name}();\n`;
  code += `${indent}        }\n`;
  code += `${indent}        return new ${name}(reader);\n`;
  code += `${indent}    };\n\n`;
  
  code += `${indent}    ${name}.toObject = function toObject(message) {\n`;
  code += `${indent}        return message;\n`;
  code += `${indent}    };\n\n`;
  
  code += `${indent}    return ${name};\n`;
  code += `${indent}})();\n\n`;
  
  return code;
}

// Process all messages in the package
for (const type of ns.nestedArray) {
  if (type instanceof protobuf.Type) {
    output += generateMessage(type, '    ');
  }
}

output += `    return ${namespace};\n`;
output += `})();\n\n`;
output += `module.exports = $root;\n`;

fs.writeFileSync(outputJs, output, 'utf8');
console.log(`Output: ${outputJs} (${output.length} bytes, ${ns.nestedArray.length} messages)`);
