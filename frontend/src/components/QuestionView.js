import React, { Component } from "react";
import "../stylesheets/App.css";
import Question from "./Question";
import Search from "./Search";
import $ from "jquery";

const base_url = "http://127.0.0.1:5000";
class QuestionView extends Component {
  constructor() {
    super();
    this.state = {
      questions: [],
      page: 1,
      totalQuestions: 0,
      categories: {},
      currentCategory: null,
    };
  }

  componentDidMount() {
    this.getQuestions();
  }

  getQuestions = () => {
    $.ajax({
      url: `${base_url}/questions?page=${this.state.page}`, // update request URL
      type: "GET",
      success: (result) => {
        console.log(result);
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          categories: result.categories,
          currentCategory: result.current_category,
        });
        return;
      },
      error: (error) => {
        alert("Unable to load questions. Please try your request again");
        return;
      },
    });
  };

  selectPage(num) {
    this.setState({ page: num }, () => this.getQuestions());
  }

  createPagination() {
    let pageNumbers = [];
    let maxPage = Math.ceil(this.state.totalQuestions / 10);
    for (let i = 1; i <= maxPage; i++) {
      pageNumbers.push(
        <span
          key={i}
          className={`page-num ${i === this.state.page ? "active" : ""}`}
          onClick={() => {
            this.selectPage(i);
          }}
        >
          {i}
        </span>
      );
    }
    return pageNumbers;
  }

  getByCategory = (id) => {
    $.ajax({
      url: `${base_url}/categories/${id}/questions`, // update request URL
      type: "GET",
      success: (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          currentCategory: result.current_category,
        });
        return;
      },
      error: (error) => {
        alert("Unable to load questions. Please try your request again");
        return;
      },
    });
  };

  submitSearch = (searchTerm) => {
    $.ajax({
      url: `${base_url}/questions/search`, // update request URL
      type: "POST",
      dataType: "json",
      contentType: "application/json",
      data: JSON.stringify({ searchTerm: searchTerm }),
      // xhrFields: {
      //   withCredentials: true,
      // },
      crossDomain: true,
      Accept: "*/*",
      success: (result) => {
        this.setState({
          questions: result.questions,
          totalQuestions: result.total_questions,
          currentCategory: result.current_category,
        });
        return;
      },
      error: (error) => {
        alert("Unable to load questions. Please try your request again");
        return;
      },
    });
  };

  questionAction = (id) => (action) => {
    if (action === "DELETE") {
      if (window.confirm("are you sure you want to delete the question?")) {
        $.ajax({
          url: `${base_url}/questions/${id}`, // update request URL
          type: "DELETE",
          success: (result) => {
            this.getQuestions();
          },
          error: (error) => {
            alert("Unable to load questions. Please try your request again");
            return;
          },
        });
      }
    }
  };

  render() {
    return (
      <div className="question-view">
        <div className="categories-list">
          <h2
            onClick={() => {
              this.getQuestions();
            }}
          >
            Categories
          </h2>
          <ul>
            {Object.keys(this.state.categories).map((index) => (
              <li
                key={index}
                onClick={() => {
                  this.getByCategory(this.state.categories[index].id);
                }}
              >
                {this.state.categories[index].type}
                {/* <img
                  className="category"
                  alt={`${this.state.categories[id]}`}
                  src={`${this.state.categories[id]}.svg`}
                /> */}
              </li>
            ))}
          </ul>
          <Search submitSearch={this.submitSearch} />
        </div>
        <div className="questions-list">
          <h2>Questions</h2>
          {this.state.questions.map((q, ind) => (
            <Question
              key={q.id}
              question={q.question}
              answer={q.answer}
              category={this.state.categories[q.category]}
              difficulty={q.difficulty}
              questionAction={this.questionAction(q.id)}
            />
          ))}
          <div className="pagination-menu">{this.createPagination()}</div>
        </div>
      </div>
    );
  }
}

export default QuestionView;