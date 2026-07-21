// Declarative pipeline: smoke gate first, then API + cross-browser UI regression in parallel.
// Needs a Linux agent with Python 3.12, Chrome, Firefox and Edge (or set GRID_URL to use a Selenium Grid).
pipeline {
    agent any

    parameters {
        choice(name: 'SUITE', choices: ['regression', 'smoke'], description: 'Which marker set to run')
        string(name: 'GRID_URL', defaultValue: '', description: 'Optional Selenium Grid, e.g. http://grid:4444/wd/hub')
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    triggers {
        cron('H 6 * * 1-5')   // nightly regression on weekdays
    }

    environment {
        GRID_ARGS = "${params.GRID_URL ? "--grid-url ${params.GRID_URL}" : ''}"
    }

    stages {
        stage('Setup') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install -q -r requirements-test.txt
                '''
            }
        }

        stage('Smoke') {
            steps {
                sh '. .venv/bin/activate && pytest -m smoke -n auto ${GRID_ARGS} --junitxml=reports/smoke.xml'
            }
        }

        stage('Regression') {
            when { expression { params.SUITE == 'regression' } }
            parallel {
                stage('API') {
                    steps {
                        sh '. .venv/bin/activate && pytest -m api -n auto --junitxml=reports/api.xml'
                    }
                }
                stage('Chrome') {
                    steps {
                        sh '. .venv/bin/activate && pytest -m ui --browser chrome -n 3 ${GRID_ARGS} --junitxml=reports/ui-chrome.xml --html=reports/ui-chrome.html --self-contained-html'
                    }
                }
                stage('Firefox') {
                    steps {
                        sh '. .venv/bin/activate && pytest -m ui --browser firefox -n 3 ${GRID_ARGS} --junitxml=reports/ui-firefox.xml --html=reports/ui-firefox.html --self-contained-html'
                    }
                }
                stage('Edge') {
                    steps {
                        sh '. .venv/bin/activate && pytest -m ui --browser edge -n 3 ${GRID_ARGS} --junitxml=reports/ui-edge.xml --html=reports/ui-edge.html --self-contained-html'
                    }
                }
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true, testResults: 'reports/*.xml'
            archiveArtifacts allowEmptyArchive: true, artifacts: 'reports/**'
        }
        failure {
            echo 'Failures: open the HTML report artifacts for screenshots of each failed UI test.'
        }
    }
}
