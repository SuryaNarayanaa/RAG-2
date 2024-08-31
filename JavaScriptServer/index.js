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
const db = new pg.Client({
  user: process.env.user,
  host: process.env.host,
  database: process.env.database,
  password: process.env.password,
  port: process.env.port,
});

db.connect();

db.query("create table if not exists chat (id serial primary key, chatname text);");
db.query("create table if not exists chatmesages (id serial primary key, message text,response text,chatid integer references chat(id));");
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

const app = express();
app.use(express.static("public"));
app.use(bodyParser.urlencoded({extended:"true"}));

app.get("/",async(req,res)=>{
  chatnames = await db.query("select * from chat order by id desc");
  if(chatnames.rows.length===0){
    chatnames = undefined;
  }
  res.render("index.ejs", {
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
  chat = await db.query("select * from chatmesages where chatid=$1",[chatid]);
  if(chat.rows.length==0){
    chat = undefined;
  }
  res.render("index.ejs", {
    chatnames:chatnames ? chatnames.rows : chatnames,
    chatname: chatname ? chatname : undefined,
    chat: chat ? chat.rows : undefined,
  });
})

app.get("/pdfchats",async (req,res)=>{
  const {chatid} = req.query;
  curr_chatid = chatid;
  chat = await db.query("select * from chatmesages where chatid=$1",[chatid]);
  if(chat.rows.length==0){
    chat = undefined;
  }
  res.render("chatwithpdf.ejs", {
    chatnames:chatnames ? chatnames.rows : chatnames,
    chatname: chatname ? chatname : undefined,
    chat: chat ? chat.rows : undefined,
  });
})

app.get("/chatwithpdf",async (req,res)=>{
  chatnames = await db.query("select * from chat order by id desc");
  if(chatnames.rows.length===0){
    chatnames = undefined;
  }
  res.render("chatwithpdf.ejs", {
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
    const response = await axios.post("https://gbrh7rr7-5000.inc1.devtunnels.ms/upload/chat",{
      question:message,
      chat_id:curr_chatid
    });
    //must delete the pdf after the a response
    await db.query("insert into chatmesages (message,response,chatid) values ($1,$2,$3)",[message,response.data.response,chatid]);
    res.redirect(`/pdfchats?chatid=${chatid}`);
  }catch(error){
    console.log(error);
    res.render("error404.ejs" , {error : "Bad Request"});

  }
})

app.post("/chat" , async (req,res)=>{
  const chatid = curr_chatid;
  const message = req.body.message;
  try{
    const response = await axios.post("https://gbrh7rr7-5000.inc1.devtunnels.ms/",{
      question:message,
    });
    await db.query("insert into chatmesages (message,response,chatid) values ($1,$2,$3)",[message,response.data.response,chatid]);
    res.redirect(`/chats?chatid=${chatid}`);
  }catch(error){
    console.log(error);
    res.render("error404.ejs" , {error : "Bad Request"});

  }
})

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
    const response = await axios.post('https://gbrh7rr7-5000.inc1.devtunnels.ms/upload', form, {
      headers: {
        ...form.getHeaders() // Include the form headers
      },
      timeout: 6000000
    });
    res.redirect(`/pdfchats?chatid=${chat_id}`);
  } catch (error) {
    console.error('Error sending file and chat_id to another API:', error);
    res.status(500).send('Error sending file and chat_id to another API.');
  }
});

app.listen(PORT,()=>console.log('Server is running'));
