import express from 'express'
import pg from 'pg';
import bodyParser from 'body-parser';
import axios from 'axios';
import dotenv from 'dotenv';
import multer from 'multer';
import path from 'path';
import FormData from 'form-data';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const PORT =3000;

dotenv.config();

const flaskurl = "http://127.0.0.1:5000";

const db = new pg.Client({
  user: process.env.user,
  host: process.env.host,
  database: process.env.database,
  password: process.env.password,
  port: process.env.port,
});

db.connect();

db.query("create table if not exists chat (id serial primary key, chatname text);");
db.query("create table if not exists chatmesages (id serial primary key, message text,response text,chatid integer references chat(id),input_img bytea,output_img bytea,flowchart bytea,csv_data text);");
db.query("create table if not exists reviews (id serial primary key, name text, review text);");

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/');
  },
  filename: function (req, file, cb) {
    cb(null, file.originalname);
  }
});

const upload = multer({ storage: storage });

let chat;
let chatname;
let chatnames;
let curr_chatid;
let input_img;
let output_img;
let flowchart;
let csv_data;

const app = express();
app.use(express.static("public"));
app.use(bodyParser.urlencoded({extended:"true"}));

app.get("/",async(req,res)=>{
  chatnames = await db.query("select * from chat order by id desc");
  if(chatnames.rows.length===0){
    chatnames = undefined;
  }
  res.render("home.ejs", {
    chatnames:chatnames ? chatnames.rows : chatnames,
    chatname:undefined,
    chat:undefined,
  });
})

app.get("/review",(req,res)=>{
  res.render("review.ejs");
})

app.post("/review",async (req,res)=>{
  const {username,review} = req.body;
  await db.query("insert into reviews (name,review) values ($1,$2)",[username,review]);
  res.redirect("/");
})

app.get("/chats",async (req,res)=>{
  const {chatid} = req.query;
  curr_chatid = chatid;
  input_img = await db.query("select input_img from chatmesages where chatid=$1",[chatid]);
  output_img = await db.query("select output_img from chatmesages where chatid=$1",[chatid]);
  flowchart = await db.query("select flowchart from chatmesages where chatid=$1",[chatid]);
  chat = await db.query("select * from chatmesages where chatid=$1",[chatid]);
  csv_data = await db.query("select csv_data from chatmesages where chatid=$1",[chatid]);
  if (input_img.rows.length === 0) {
    input_img = undefined;
  } else {
    input_img = input_img.rows.map(row =>{
      return row.input_img ? row.input_img.toString('base64') : null;
    });
  }

  if (output_img.rows.length === 0) {
    output_img = undefined;
  } else {
    output_img = output_img.rows.map(row => {
      return row.output_img ? row.output_img.toString('base64') : null;
    });
  }

  if (flowchart.rows.length === 0) {
    flowchart = undefined;
  } else {
    flowchart = flowchart.rows.map(row => {
      return row.flowchart ? row.flowchart.toString('base64') : null;
    });
  }
  if(chat.rows.length===0){
    chat = undefined;
  }

  if(csv_data.rows.length===0){
    csv_data = undefined;
  }

  res.render("index.ejs", {
    chatnames:chatnames ? chatnames.rows : chatnames,
    chatname: chatname ? chatname : undefined,
    chat: chat ? chat.rows : undefined,
    input_img: input_img,
    output_img: output_img,
    flowchart: flowchart,
    csv_data: csv_data ? csv_data.rows:undefined,
  });
})

app.get("/pdfchats",async (req,res)=>{
  const {chatid} = req.query;
  curr_chatid = chatid;
  input_img = await db.query("select input_img from chatmesages where chatid=$1",[chatid]);
  output_img = await db.query("select output_img from chatmesages where chatid=$1",[chatid]);
  flowchart = await db.query("select flowchart from chatmesages where chatid=$1",[chatid]);
  chat = await db.query("select * from chatmesages where chatid=$1",[chatid]);
  if (input_img.rows.length === 0) {
    input_img = undefined;
  } else {
    input_img = input_img.rows.map(row =>{
      return row.input_img ? row.input_img.toString('base64') : null;
    });
  }

  if (output_img.rows.length === 0) {
    output_img = undefined;
  } else {
    output_img = output_img.rows.map(row => {
      return row.output_img ? row.output_img.toString('base64') : null;
    });
  }

  if (flowchart.rows.length === 0) {
    flowchart = undefined;
  } else {
    flowchart = flowchart.rows.map(row => {
      return row.flowchart ? row.flowchart.toString('base64') : null;
    });
  }
  if(chat.rows.length===0){
    chat = undefined;
  }

  res.render("chatwithpdf.ejs", {
    chatnames:chatnames ? chatnames.rows : chatnames,
    chatname: chatname ? chatname : undefined,
    chat: chat ? chat.rows : undefined,
    input_img: input_img,
    output_img: output_img,
    flowchart: flowchart,
  });
})

app.get("/chatwithpdf",async (req,res)=>{
  chatnames = await db.query("select * from chat order by id desc");
  if(chatnames.rows.length===0){
    chatnames = undefined;
  }
  res.render("pdfchathome.ejs", {
    chatnames:chatnames ? chatnames.rows : chatnames,
    chatname:undefined,
    chat:undefined,
  });
})

app.post("/newchat" , async (req,res)=>{
  const {chatname} = req.body;
  try {
    await db.query("insert into chat (chatname) values ($1)",[chatname]);
    res.redirect("/");
  } catch (error) {
    console.log(error);
    res.render("error404.ejs");
  }

})

app.post("/chatwithpdf" , async (req,res)=>{
  const chatid = curr_chatid;
  const message = req.body.message;
  try{
    const response = await axios.post(`${flaskurl}/upload/chat`,{
      question:message,
      chat_id:curr_chatid
    });
    await db.query("insert into chatmesages (message,response,chatid) values ($1,$2,$3)",[message,response.data.response,chatid]);
    res.redirect(`/pdfchats?chatid=${chatid}`);
  }catch(error){
    console.log(error);
    res.render("error404.ejs" , {error : "Bad Request"});

  }
})

app.post("/chat", upload.single('imgfile'), async (req, res) => {
  const chatid = curr_chatid;
  const message = req.body.message;
  const imgfile = req.file;
  const enableImages = req.body['enable-images'] === 'on';
  const enableFlowchart = req.body['enable-flowchart'] === 'on';
  const enableTable = req.body['enable-table'] === 'on';
  let return_img = undefined;
  let return_flowchart = undefined;
  let return_table = undefined;

  //For Debugging
  console.log('Message:', message);
  console.log('Enable Images:', enableImages);
  console.log('Enable Flowchart:', enableFlowchart);
  console.log('Enable Table:', enableTable);

  try {
    const form = new FormData();
    form.append('question', message);

    if (imgfile) {
      form.append('image', fs.createReadStream(imgfile.path));
    }
    if (enableImages && !imgfile) {
      return_img = "text";
    }
    else if(enableImages && imgfile){
      return_img = "image";
    }

    if(enableTable){
      return_table = "true";
    }

    if(return_img){
      form.append('return_img', return_img);
    }
    if(return_table){
      form.append('return_table', return_table);
    }
    form.append('return_flowchart', enableFlowchart ? 'true' : 'false');

    const inputImageData = imgfile ? fs.readFileSync(imgfile.path) : null;

    if (message && imgfile && !(return_flowchart && return_img)) {
      const response = await axios.post(`${flaskurl}/`, form, {
        headers: form.getHeaders()
      });
      await db.query("INSERT INTO chatmesages (message, input_img, response, chatid) VALUES ($1, $2, $3, $4)", [message, inputImageData, response.data.response, chatid]);
    }else if(return_table && message){
      const response = await axios.post(`${flaskurl}/`,form, {
        headers: form.getHeaders()
      });
      await db.query("INSERT INTO chatmesages (message, chatid, csv_data) VALUES ($1, $2, $3)", [message, chatid, response.data]);
    }else if (enableImages && !imgfile) {
      const response = await axios.post(`${flaskurl}/`,form, {
        headers: form.getHeaders(),
        responseType: 'arraybuffer'
      });
      const binaryData = Buffer.from(response.data);
      await db.query("INSERT INTO chatmesages (message, chatid, output_img) VALUES ($1, $2, $3)", [message, chatid, binaryData]);
    } else if (enableImages && imgfile) {
      const response = await axios.post(`${flaskurl}/`,form, {
        headers: form.getHeaders(),
        responseType: 'arraybuffer'
      });
      const binaryData = Buffer.from(response.data);
      await db.query("INSERT INTO chatmesages (chatid, input_img, output_img) VALUES ($1, $2, $3)", [chatid, inputImageData,binaryData]);
    } else if (enableFlowchart) {
      const response = await axios.post(`${flaskurl}/`,form, {
        headers: form.getHeaders(),
        responseType: 'arraybuffer'
      });
      const binaryData = Buffer.from(response.data);
      await db.query("INSERT INTO chatmesages (message, chatid, flowchart) VALUES ($1, $2, $3)", [message, chatid, binaryData]);
    } else {
      const response = await axios.post(`${flaskurl}/`, form, {
        headers: form.getHeaders()
      });
      await db.query("INSERT INTO chatmesages (message, response, chatid) VALUES ($1, $2, $3)", [message, response.data.response, chatid]);
    }

    res.redirect(`/chats?chatid=${chatid}`);
  } catch (error) {
    console.log(error);
    res.render("error404.ejs", { error: "Bad Request" });
  }
});

app.post('/uploadpdf', upload.single('pdfFile'), async (req, res) => {
  if (!req.file) {
    return res.status(400).send('No file uploaded.');
  }

  const filePath = path.join(__dirname, 'uploads', req.file.filename);
  const chat_id = curr_chatid;
  try {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    form.append('chat_id', chat_id);
    const response = await axios.post(`${flaskurl}/upload`, form, {
      headers: {
        ...form.getHeaders()
      }
    });

    res.redirect(`/pdfchats?chatid=${chat_id}`);
  } catch (error) {
    console.error('Error sending file and chat_id to Flask Server:', error);
    res.status(500).send('Error sending file to Flask Server');
  }
});

app.post("/deletechat",async (req,res)=>{
  const {chatid} = req.body;
  await db.query("delete from chatmesages where chatid=$1",[chatid]);
  await db.query("delete from chat where id=$1",[chatid]);
  res.redirect("/");
});

app.listen(PORT,()=>console.log(`Server is running on http://localhost:${PORT}`));
